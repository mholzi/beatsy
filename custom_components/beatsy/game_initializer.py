"""
Beatsy Game Initialization Module

Handles game session creation, state reset, and ID generation for new games.
Provides atomic initialization operations with rollback capability.

Story 3.5: Task 4 - Game State Reset and Session Creation (AC-2, AC-4, AC-5, AC-6)
Story 7.1: Spotify Playlist Track Fetching with Pagination
"""

import copy
import logging
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Optional

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN
from .spotify_helper import (
    fetch_playlist_tracks,
    extract_track_metadata,
    SpotifyPlaylistNotFound,
    SpotifyAPIError,
)

_LOGGER = logging.getLogger(__name__)


@dataclass
class PlaylistMetadata:
    """
    Playlist loading metadata for admin feedback.

    Story 7.2: Provides detailed information about playlist loading results,
    including filtered track counts for quality assessment.
    """

    playlist_id: str
    playlist_name: str
    total_tracks: int  # Total tracks in Spotify playlist
    loaded_tracks: int  # Tracks successfully loaded with year data
    filtered_tracks: int  # Tracks excluded (missing year)
    load_timestamp: datetime


@dataclass
class GameConfigInput:
    """
    Admin-provided game configuration input.

    Story 3.5: AC-4 (Game Configuration Storage)
    Validates all game settings before initialization.
    """

    media_player: str  # Entity ID (e.g., "media_player.spotify_living_room")
    playlist_id: str  # Playlist file ID (e.g., "80s_hits")
    timer_duration: int = 30  # Round timer in seconds (10-120 range)
    year_range_min: int = 1950  # Minimum year for filtering
    year_range_max: int = 2024  # Maximum year for filtering
    exact_points: int = 10  # Points for exact year match
    close_points: int = 5  # Points for ±2 years
    near_points: int = 2  # Points for ±5 years
    bet_multiplier: int = 2  # Multiplier when betting (1-10x)

    def validate(self) -> list[str]:
        """
        Validate configuration and return list of error messages.

        Returns:
            List of error messages (empty if valid)

        Example:
            >>> config = GameConfigInput(media_player="", playlist_id="test")
            >>> errors = config.validate()
            >>> print(errors)
            ['Media player selection required']
        """
        errors = []

        # Media player validation
        if not self.media_player or self.media_player.strip() == "":
            errors.append("Media player selection required")

        # Playlist validation
        if not self.playlist_id or self.playlist_id.strip() == "":
            errors.append("Playlist selection required")

        # Timer validation
        if not (10 <= self.timer_duration <= 120):
            errors.append("Timer must be between 10-120 seconds")

        # Year range validation
        current_year = datetime.now().year
        if not (1900 <= self.year_range_min <= current_year):
            errors.append(f"Year min must be between 1900-{current_year}")

        if not (1900 <= self.year_range_max <= current_year):
            errors.append(f"Year max must be between 1900-{current_year}")

        if self.year_range_min >= self.year_range_max:
            errors.append("Year min must be less than year max")

        # Scoring validation
        if not (0 <= self.exact_points <= 100):
            errors.append("Exact points must be between 0-100")

        if not (0 <= self.close_points <= 100):
            errors.append("Close points must be between 0-100")

        if not (0 <= self.near_points <= 100):
            errors.append("Near points must be between 0-100")

        # Bet multiplier validation
        if not (1 <= self.bet_multiplier <= 10):
            errors.append("Bet multiplier must be between 1-10")

        return errors


def reset_game_state(hass: HomeAssistant) -> None:
    """
    Clear all previous game state to prepare for new game session.

    Story 3.5: AC-2 (Game State Reset on Start)
    Clears all dynamic game state while preserving configuration.

    Args:
        hass: Home Assistant instance

    Note:
        This is an idempotent operation - safe to call multiple times.
        Handles missing keys gracefully (no exceptions).

    Example:
        >>> reset_game_state(hass)
        # All game state keys cleared
    """
    # Initialize domain data if not exists
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    # Clear all dynamic game state
    hass.data[DOMAIN]["players"] = []
    hass.data[DOMAIN]["current_round"] = None
    hass.data[DOMAIN]["played_songs"] = []
    hass.data[DOMAIN]["round_history"] = []
    hass.data[DOMAIN]["scores"] = {}

    # Clear previous game session data
    if "game_id" in hass.data[DOMAIN]:
        old_game_id = hass.data[DOMAIN]["game_id"]
        _LOGGER.info("Invalidating previous game session: %s", old_game_id)
        hass.data[DOMAIN].pop("game_id", None)

    # Story 3.6 Task 12: Invalidate old admin key (AC-9)
    # New admin key will be generated by generate_admin_key() in create_game_session()
    if "admin_key" in hass.data[DOMAIN]:
        old_admin_key = hass.data[DOMAIN]["admin_key"]
        _LOGGER.info("Invalidating previous admin key: %s...", old_admin_key[:8])
        hass.data[DOMAIN].pop("admin_key", None)
        hass.data[DOMAIN].pop("admin_key_expiry", None)

    _LOGGER.info("Game state reset completed")


def generate_game_id() -> str:
    """
    Generate unique game session identifier using UUID v4.

    Story 3.5: AC-2 (New game_id generation)

    Returns:
        UUID v4 string (e.g., "550e8400-e29b-41d4-a716-446655440000")

    Example:
        >>> game_id = generate_game_id()
        >>> len(game_id)
        36
        >>> game_id.count('-')
        4
    """
    game_id = str(uuid.uuid4())
    _LOGGER.debug("Generated game_id: %s", game_id)
    return game_id


def generate_admin_key() -> tuple[str, datetime]:
    """
    Generate unique admin key with 24-hour expiry for device-specific admin privileges.

    Story 3.5: AC-6 (Admin Key Generation)
    Admin key allows the game creator to join as a player using their device.

    Returns:
        Tuple of (admin_key: str, expiry: datetime)
        - admin_key: UUID v4 string
        - expiry: Datetime exactly 24 hours from now

    Example:
        >>> admin_key, expiry = generate_admin_key()
        >>> len(admin_key)
        36
        >>> expiry > datetime.now()
        True
    """
    admin_key = str(uuid.uuid4())
    expiry = datetime.now() + timedelta(hours=24)

    # Log first 8 characters only for security
    _LOGGER.info("Generated admin_key: %s... (expires in 24 hours)", admin_key[:8])

    return admin_key, expiry


def validate_admin_key(hass: HomeAssistant, admin_key: str, game_id: Optional[str] = None) -> bool:
    """
    Validate admin key for player registration.

    Story 3.6 Task 5: AC-3 (Admin Key Validation)
    Checks if provided admin_key matches stored key and hasn't expired.

    Args:
        hass: Home Assistant instance
        admin_key: Admin key from player registration request
        game_id: Optional game ID for validation (currently unused, reserved for multi-game support)

    Returns:
        bool: True if admin_key is valid and not expired, False otherwise

    Example:
        >>> validate_admin_key(hass, "valid-uuid-key")
        True
        >>> validate_admin_key(hass, "expired-key")
        False
    """
    if not admin_key:
        _LOGGER.debug("Admin key validation failed: No key provided")
        return False

    # Get current game session data
    if DOMAIN not in hass.data:
        _LOGGER.warning("Admin key validation failed: No game session exists")
        return False

    session_data = hass.data[DOMAIN]

    # Check if admin key exists in session
    stored_admin_key = session_data.get("admin_key")
    if not stored_admin_key:
        _LOGGER.warning("Admin key validation failed: No admin key in session")
        return False

    # Validate key matches
    if admin_key != stored_admin_key:
        _LOGGER.warning(
            "Admin key validation failed: Key mismatch (provided: %s..., stored: %s...)",
            admin_key[:8],
            stored_admin_key[:8]
        )
        return False

    # Check expiry
    admin_key_expiry = session_data.get("admin_key_expiry")
    if not admin_key_expiry:
        _LOGGER.warning("Admin key validation failed: No expiry timestamp in session")
        return False

    now = datetime.now()
    if now > admin_key_expiry:
        _LOGGER.warning(
            "Admin key validation failed: Key expired (expired at: %s, now: %s)",
            admin_key_expiry.isoformat(),
            now.isoformat()
        )
        return False

    # All checks passed
    _LOGGER.info("Admin key validated successfully: %s...", admin_key[:8])
    return True


async def load_spotify_playlist(
    hass: HomeAssistant, playlist_uri: str
) -> tuple[list[dict[str, Any]], PlaylistMetadata]:
    """Load and process tracks from Spotify playlist.

    Story 7.1: Fetches playlist tracks via Spotify API and extracts metadata.
    Story 7.2: Filters tracks without year and returns metadata with filtered counts.

    Args:
        hass: Home Assistant instance
        playlist_uri: Spotify playlist URI (spotify:playlist:xxx or URL)

    Returns:
        Tuple of (tracks, metadata):
            - tracks: List of track dictionaries with metadata: {uri, title, artist, album, year, cover_url}
            - metadata: PlaylistMetadata with filtered track counts

    Raises:
        SpotifyPlaylistNotFound: If playlist URI is invalid or inaccessible
        SpotifyAPIError: If API communication fails
        ValueError: If playlist URI format is invalid or no playable tracks found
    """
    # Story 7.1 AC-1: Fetch all tracks from Spotify playlist with pagination
    _LOGGER.info("Loading Spotify playlist: %s", playlist_uri)

    try:
        raw_tracks, playlist_name, playlist_id = await fetch_playlist_tracks(hass, playlist_uri)
    except (SpotifyPlaylistNotFound, SpotifyAPIError, ValueError) as e:
        _LOGGER.error("Failed to load Spotify playlist: %s", str(e))
        raise

    total_tracks = len(raw_tracks)

    if not raw_tracks:
        _LOGGER.warning("Spotify playlist is empty: %s", playlist_uri)
        metadata = PlaylistMetadata(
            playlist_id=playlist_id,
            playlist_name=playlist_name,
            total_tracks=0,
            loaded_tracks=0,
            filtered_tracks=0,
            load_timestamp=datetime.now()
        )
        return [], metadata

    # Story 7.2 AC-1: Extract metadata from each track
    _LOGGER.info("Extracting metadata from %d tracks", total_tracks)
    tracks_with_metadata = []
    filtered_tracks = 0

    for raw_track in raw_tracks:
        metadata_dict = extract_track_metadata(raw_track)

        # Story 7.2 AC-2: Filter tracks without year
        if not metadata_dict.get('year'):
            filtered_tracks += 1
            _LOGGER.warning(
                "Track '%s' by '%s' skipped - missing release year",
                metadata_dict.get('title', 'Unknown'),
                metadata_dict.get('artist', 'Unknown')
            )
            continue

        # Story 7.2 AC-1: Add to available_songs list
        tracks_with_metadata.append(metadata_dict)

    # Story 7.2 AC-3: Report filtered track count
    if filtered_tracks > 0:
        _LOGGER.info(
            "Loaded %d of %d tracks (%d filtered - missing year)",
            len(tracks_with_metadata),
            total_tracks,
            filtered_tracks
        )

    # Story 7.2: Check if no playable tracks found
    if not tracks_with_metadata:
        raise ValueError(
            f"No playable tracks found. All tracks are missing release year data "
            f"(total tracks: {total_tracks}, filtered: {filtered_tracks})"
        )

    # Story 7.2: Create PlaylistMetadata for admin response
    playlist_metadata = PlaylistMetadata(
        playlist_id=playlist_id,
        playlist_name=playlist_name,
        total_tracks=total_tracks,
        loaded_tracks=len(tracks_with_metadata),
        filtered_tracks=filtered_tracks,
        load_timestamp=datetime.now()
    )

    _LOGGER.info(
        "Successfully loaded %d tracks from playlist '%s'",
        len(tracks_with_metadata),
        playlist_name
    )

    return tracks_with_metadata, playlist_metadata


async def create_game_session(
    hass: HomeAssistant, config: dict[str, Any], playlist_data: dict[str, Any]
) -> dict[str, Any]:
    """
    Create a new game session with full state initialization.

    Story 3.5: AC-2, AC-4, AC-5, AC-6
    Story 11.1: Persists configuration to HA storage
    Atomic operation: Either fully succeeds or leaves state unchanged.

    Args:
        hass: Home Assistant instance
        config: Validated game configuration dict matching GameConfigInput structure
        playlist_data: Loaded playlist dict with 'songs' array (already year-filtered)

    Returns:
        Session data dict with structure:
        {
            "game_id": str,
            "admin_key": str,
            "admin_key_expiry": datetime,
            "status": "lobby",
            "player_count": 0,
            "songs_total": int,
            "songs_remaining": int
        }

    Raises:
        ValueError: If config validation fails or playlist data invalid

    Example:
        >>> config = {"media_player": "media_player.spotify", ...}
        >>> playlist = {"playlist_name": "80s Hits", "songs": [...]}
        >>> session = await create_game_session(hass, config, playlist)
        >>> session['status']
        'lobby'
    """
    from .game_state import get_game_state, save_config

    # Step 1: Get the existing game state (initialized during component setup)
    try:
        state = get_game_state(hass)
    except ValueError:
        # If no state exists, initialize domain but this shouldn't happen in normal flow
        if DOMAIN not in hass.data:
            hass.data[DOMAIN] = {}
        from .game_state import init_game_state
        state = init_game_state(hass, "default")

    # Step 2: Generate new game identifiers
    game_id = generate_game_id()
    admin_key, admin_key_expiry = generate_admin_key()

    # Step 3: Update game state configuration
    state.game_config = {
        "media_player": config["media_player"],
        "playlist_id": config["playlist_id"],
        "timer_duration": config.get("timer_duration", 30),
        "year_range_min": config.get("year_range_min", 1950),
        "year_range_max": config.get("year_range_max", 2024),
        "exact_points": config.get("exact_points", 10),
        "close_points": config.get("close_points", 5),
        "near_points": config.get("near_points", 2),
        "bet_multiplier": config.get("bet_multiplier", 2),
        "game_id": game_id,  # Include game_id for tracking
    }

    # Story 11.1: AC-1 - Persist config to HA storage immediately
    await save_config(hass, state.game_config, state.entry_id)
    _LOGGER.debug("Config persisted to storage for entry %s", state.entry_id)

    # Step 4: Store playlist songs and enrich with Spotify metadata
    songs = playlist_data.get("songs", [])

    # Enrich songs with Spotify metadata (fetch title, artist, album, cover_url)
    enriched_songs = []
    spotify_helper = state.spotify

    for song in songs:
        # If song already has full metadata, use as-is
        if all(field in song for field in ["uri", "title", "artist", "album", "cover_url"]):
            enriched_songs.append(song)
            continue

        # Otherwise, fetch from Spotify
        spotify_uri = song.get("spotify_uri") or song.get("uri")
        if not spotify_uri:
            _LOGGER.warning("Song missing spotify_uri, skipping: %s", song)
            continue

        try:
            # Extract track ID from URI (spotify:track:ID)
            track_id = spotify_uri.split(":")[-1]

            # Fetch track data from Spotify
            # Note: This requires spotify integration to be set up
            # For now, create a minimal enriched song with available data
            enriched_song = {
                "uri": spotify_uri,
                "title": song.get("title", "Unknown"),
                "artist": song.get("artist", "Unknown"),
                "album": song.get("album", "Unknown"),
                "year": song.get("year", 2000),
                "cover_url": song.get("cover_url", ""),
                "fun_fact": song.get("fun_fact", ""),
                "spotify_uri": spotify_uri,
            }
            enriched_songs.append(enriched_song)

        except Exception as e:
            _LOGGER.warning("Failed to enrich song %s: %s", spotify_uri, e)
            continue

    state.available_songs = enriched_songs.copy()  # Make a copy to avoid mutations

    # Story 5.7: Store original playlist for reset_game() to restore available_songs
    state.original_playlist = copy.deepcopy(enriched_songs)

    # Step 5: Reset dynamic state for new game
    state.players = []
    state.current_round = None
    state.played_songs = []

    # Step 6: Set game status and timestamps
    state.game_status = "lobby"
    state.game_started = True
    state.game_started_at = time.time()  # CRITICAL: Set timestamp for game_id generation

    # Step 7: Store admin key in legacy location for backward compatibility
    # (websocket_api and other modules may still reference hass.data[DOMAIN]["admin_key"])
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    hass.data[DOMAIN]["admin_key"] = admin_key
    hass.data[DOMAIN]["admin_key_expiry"] = admin_key_expiry

    _LOGGER.info(
        "Game session created: game_id=%s, status=lobby, songs=%d, started_at=%f",
        game_id,
        len(songs),
        state.game_started_at,
    )

    # Return session data for API response
    return {
        "game_id": game_id,
        "admin_key": admin_key,
        "admin_key_expiry": admin_key_expiry,
        "status": "lobby",
        "player_count": 0,
        "songs_total": len(songs),
        "songs_remaining": len(songs),
    }
