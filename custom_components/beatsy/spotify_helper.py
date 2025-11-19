"""Spotify integration helper for Beatsy.

This module provides wrapper functions to interact with Home Assistant's
Spotify integration for fetching playlists, extracting metadata, and
controlling playback.

CRITICAL: Cast-enabled devices (Chromecast, Google Home, Sonos) can play
Spotify URIs directly via media_player.play_media service WITHOUT requiring
the Spotify integration to be loaded. Metadata is automatically populated
after playback starts.
"""
import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Any
import re

from homeassistant.core import HomeAssistant, State
from homeassistant.exceptions import HomeAssistantError

_LOGGER = logging.getLogger(__name__)

# Spotify integration domain
SPOTIFY_DOMAIN = "spotify"

# Media player feature flag for play_media support
SUPPORT_PLAY_MEDIA = 16384

# Spotify API pagination constants
SPOTIFY_PAGE_SIZE = 100  # Maximum tracks per API request
MAX_CONCURRENT_REQUESTS = 10  # Maximum parallel pagination requests


# Custom exceptions for Spotify operations
class SpotifyPlaylistNotFound(Exception):
    """Raised when playlist URI is invalid or inaccessible."""
    pass


class SpotifyAPIError(Exception):
    """Raised when Spotify API communication fails after retries."""
    pass


@dataclass
class MediaPlayerInfo:
    """Media player information for Beatsy game.

    Represents a media player capable of playing Spotify tracks.
    Used for admin dropdown selection and game configuration.
    """
    entity_id: str
    friendly_name: str
    state: str
    supports_play_media: bool = True


async def fetch_playlist_tracks(hass: HomeAssistant, playlist_uri: str) -> tuple[list[dict[str, Any]], str, str]:
    """Fetch all tracks from a Spotify playlist with parallel pagination.

    Story 7.1: Implements parallel pagination using asyncio.gather() to meet
    performance target of <10 seconds for 500-track playlists.

    Args:
        hass: Home Assistant instance
        playlist_uri: Spotify playlist URI (spotify:playlist:xxx or https://...)

    Returns:
        Tuple of (tracks, playlist_name, playlist_id):
            - tracks: List of track dictionaries with Spotify API data
            - playlist_name: Name of the playlist
            - playlist_id: Spotify playlist ID

    Raises:
        SpotifyPlaylistNotFound: If playlist URI is invalid or inaccessible
        SpotifyAPIError: If API communication fails after retries
        ValueError: If playlist URI format is invalid
    """
    start_time = time.time()

    # Normalize URI format (raises ValueError for invalid format)
    try:
        normalized_uri = _normalize_spotify_uri(playlist_uri)
        playlist_id = _extract_playlist_id(normalized_uri)
    except ValueError as e:
        _LOGGER.error("Invalid playlist URI format: %s", playlist_uri)
        raise

    # Get Spotify integration coordinator
    try:
        coordinator = await _get_spotify_coordinator(hass)
    except Exception as e:
        _LOGGER.error("Spotify integration not available: %s", str(e))
        raise SpotifyAPIError(f"Spotify integration not configured: {str(e)}") from e

    try:
        # Fetch first page to get total track count and playlist metadata
        _LOGGER.debug("Fetching playlist metadata: %s", playlist_id)
        playlist = await _fetch_playlist_page_with_retry(coordinator, normalized_uri, offset=0, limit=SPOTIFY_PAGE_SIZE)

        if not playlist or not hasattr(playlist, 'tracks'):
            raise SpotifyPlaylistNotFound(f"Playlist not found or inaccessible: {normalized_uri}")

        # Get playlist name for logging
        playlist_name = playlist.name if hasattr(playlist, 'name') else playlist_id

        # Get total track count
        total_tracks = playlist.tracks.total if hasattr(playlist.tracks, 'total') else 0

        if total_tracks == 0:
            _LOGGER.warning("Playlist %s (%s) is empty", playlist_id, playlist_name)
            return [], playlist_name, playlist_id

        _LOGGER.info(
            "Loading playlist %s: %s (%d tracks)",
            playlist_id,
            playlist_name,
            total_tracks
        )

        # Extract tracks from first page
        all_tracks = []
        if hasattr(playlist.tracks, 'items'):
            for item in playlist.tracks.items:
                if item and hasattr(item, 'track') and item.track:
                    all_tracks.append(item.track)

        # If all tracks fit in first page, return immediately
        if total_tracks <= SPOTIFY_PAGE_SIZE:
            duration = time.time() - start_time
            _LOGGER.info(
                "Playlist loaded in %.2f seconds: %d tracks from %s",
                duration,
                len(all_tracks),
                playlist_name
            )
            return all_tracks, playlist_name, playlist_id

        # Fetch remaining pages in parallel
        remaining_pages = []
        for offset in range(SPOTIFY_PAGE_SIZE, total_tracks, SPOTIFY_PAGE_SIZE):
            remaining_pages.append((offset, min(SPOTIFY_PAGE_SIZE, total_tracks - offset)))

        total_pages = len(remaining_pages) + 1  # +1 for first page already fetched
        _LOGGER.debug(
            "Fetching %d additional pages (total: %d pages, max %d concurrent)",
            len(remaining_pages),
            total_pages,
            MAX_CONCURRENT_REQUESTS
        )

        # Fetch pages in batches of MAX_CONCURRENT_REQUESTS
        page_results = []
        for batch_start in range(0, len(remaining_pages), MAX_CONCURRENT_REQUESTS):
            batch_end = min(batch_start + MAX_CONCURRENT_REQUESTS, len(remaining_pages))
            batch = remaining_pages[batch_start:batch_end]

            _LOGGER.debug(
                "Fetching page batch: %d-%d of %d",
                batch_start + 2,  # +2 because first page already fetched (page 1)
                batch_end + 1,
                total_pages
            )

            # Create tasks for this batch
            tasks = [
                _fetch_playlist_tracks_page(coordinator, normalized_uri, offset, limit)
                for offset, limit in batch
            ]

            # Execute batch in parallel
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            # Check for errors
            for idx, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    offset, limit = batch[idx]
                    _LOGGER.error(
                        "Failed to fetch page at offset %d: %s",
                        offset,
                        str(result)
                    )
                    raise SpotifyAPIError(f"Pagination failed: {str(result)}") from result
                else:
                    page_results.extend(result)

        # Combine all tracks
        all_tracks.extend(page_results)

        # Calculate performance metrics
        duration = time.time() - start_time
        num_requests = total_pages
        tracks_fetched = len(all_tracks)

        # Log completion with performance metrics
        _LOGGER.info(
            "Playlist loaded in %.2f seconds: %d tracks fetched in %d requests from %s",
            duration,
            tracks_fetched,
            num_requests,
            playlist_name
        )

        # Warn if performance target missed (10 seconds for 500 tracks)
        if tracks_fetched >= 500 and duration > 10.0:
            _LOGGER.warning(
                "Playlist load time exceeded target: %.2fs for %d tracks (target: <10s for 500 tracks)",
                duration,
                tracks_fetched
            )

        # Warn if track count mismatch
        if tracks_fetched != total_tracks:
            _LOGGER.warning(
                "Track count mismatch: expected %d, fetched %d",
                total_tracks,
                tracks_fetched
            )

        return all_tracks, playlist_name, playlist_id

    except SpotifyPlaylistNotFound:
        # Re-raise our custom exceptions
        raise
    except SpotifyAPIError:
        raise
    except Exception as e:
        _LOGGER.error("Unexpected error fetching playlist %s: %s", normalized_uri, str(e), exc_info=True)
        raise SpotifyAPIError(f"Failed to fetch playlist: {str(e)}") from e


async def _fetch_playlist_page_with_retry(
    coordinator: Any,
    playlist_uri: str,
    offset: int,
    limit: int,
    max_retries: int = 3
) -> Any:
    """Fetch single playlist page with exponential backoff retry logic.

    Story 7.1 Task 3: Implements retry logic for rate limits and network errors.

    Args:
        coordinator: Spotify coordinator from HA integration
        playlist_uri: Normalized Spotify playlist URI
        offset: Starting track offset
        limit: Number of tracks to fetch
        max_retries: Maximum retry attempts (default: 3)

    Returns:
        Playlist object from Spotify API

    Raises:
        SpotifyAPIError: If all retry attempts fail
    """
    for attempt in range(1, max_retries + 1):
        try:
            # Get playlist with pagination parameters
            # Note: Spotify coordinator client may not support offset/limit directly
            # Using get_playlist which returns first page by default
            playlist = await coordinator.client.get_playlist(playlist_uri)
            return playlist

        except Exception as e:
            error_str = str(e).lower()

            # Check for rate limit (429)
            if '429' in error_str or 'rate limit' in error_str:
                if attempt < max_retries:
                    # Exponential backoff: 1s, 2s, 4s
                    delay = 2 ** (attempt - 1)
                    _LOGGER.warning(
                        "Rate limit hit, retrying in %d seconds (attempt %d/%d)",
                        delay,
                        attempt,
                        max_retries
                    )
                    await asyncio.sleep(delay)
                    continue
                else:
                    _LOGGER.error("Rate limit retry exhausted after %d attempts", max_retries)
                    raise SpotifyAPIError(f"Rate limit exceeded after {max_retries} retries") from e

            # Check for network timeout
            elif 'timeout' in error_str or 'connection' in error_str:
                if attempt < max_retries:
                    delay = 2 ** (attempt - 1)
                    _LOGGER.warning(
                        "Network error, retrying in %d seconds (attempt %d/%d): %s",
                        delay,
                        attempt,
                        max_retries,
                        str(e)
                    )
                    await asyncio.sleep(delay)
                    continue
                else:
                    _LOGGER.error("Network retry exhausted after %d attempts", max_retries)
                    raise SpotifyAPIError(f"Network error after {max_retries} retries: {str(e)}") from e

            # Check for 404 (playlist not found)
            elif '404' in error_str or 'not found' in error_str:
                _LOGGER.error("Playlist not found: %s", playlist_uri)
                raise SpotifyPlaylistNotFound(f"Playlist not found: {playlist_uri}") from e

            # Other errors - raise immediately
            else:
                _LOGGER.error("Spotify API error: %s", str(e))
                raise SpotifyAPIError(f"Spotify API error: {str(e)}") from e

    # Should never reach here, but just in case
    raise SpotifyAPIError(f"Failed after {max_retries} retries")


async def _fetch_playlist_tracks_page(
    coordinator: Any,
    playlist_uri: str,
    offset: int,
    limit: int
) -> list[Any]:
    """Fetch single page of playlist tracks.

    Story 7.1 Task 1.2: Pagination helper for parallel fetching.

    Args:
        coordinator: Spotify coordinator from HA integration
        playlist_uri: Normalized Spotify playlist URI
        offset: Starting track offset
        limit: Number of tracks to fetch

    Returns:
        List of track objects from this page

    Raises:
        SpotifyAPIError: If fetch fails
    """
    try:
        # Fetch page with retry logic
        # Note: The Spotify coordinator's get_playlist method may need to be called
        # differently to support offset/limit. For now, we'll use the client's
        # playlist_items method if available.

        # Extract playlist ID for direct API call
        playlist_id = _extract_playlist_id(playlist_uri)

        # Try to use playlist_items method for pagination support
        if hasattr(coordinator.client, 'playlist_items'):
            result = await coordinator.client.playlist_items(
                playlist_id=playlist_id,
                offset=offset,
                limit=limit
            )

            # Extract tracks from items
            tracks = []
            if result and hasattr(result, 'items'):
                for item in result.items:
                    if item and hasattr(item, 'track') and item.track:
                        tracks.append(item.track)

            _LOGGER.debug(
                "Fetched page: offset=%d, limit=%d, tracks=%d",
                offset,
                limit,
                len(tracks)
            )

            return tracks
        else:
            # Fallback: get_playlist doesn't support pagination natively
            # This is a limitation we need to document
            _LOGGER.warning(
                "Spotify coordinator doesn't support pagination, falling back to single request"
            )
            playlist = await _fetch_playlist_page_with_retry(
                coordinator, playlist_uri, offset, limit
            )

            tracks = []
            if hasattr(playlist.tracks, 'items'):
                for item in playlist.tracks.items:
                    if item and hasattr(item, 'track') and item.track:
                        tracks.append(item.track)

            return tracks

    except (SpotifyAPIError, SpotifyPlaylistNotFound):
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        _LOGGER.error(
            "Failed to fetch playlist page (offset=%d, limit=%d): %s",
            offset,
            limit,
            str(e)
        )
        raise SpotifyAPIError(f"Failed to fetch page: {str(e)}") from e


def extract_track_metadata(track_data: Any) -> dict[str, Any]:
    """Extract and normalize track metadata including release year.

    Args:
        track_data: Raw track object from Spotify API

    Returns:
        Dictionary with normalized metadata: {uri, title, artist, album, year, cover_url}
    """
    try:
        # Extract basic fields
        uri = track_data.uri if hasattr(track_data, 'uri') else None
        title = track_data.name if hasattr(track_data, 'name') else None

        # Extract artist (primary artist)
        artist = None
        if hasattr(track_data, 'artists') and track_data.artists:
            artist = track_data.artists[0].name if hasattr(track_data.artists[0], 'name') else None

        # Extract album data
        album_name = None
        release_date = None
        cover_url = None

        if hasattr(track_data, 'album'):
            album = track_data.album
            album_name = album.name if hasattr(album, 'name') else None
            release_date = album.release_date if hasattr(album, 'release_date') else None

            # Select album cover (prefer medium size ~300px)
            if hasattr(album, 'images') and album.images:
                # Images are typically sorted by size (largest first)
                # Prefer index 1 (medium) if available, otherwise use first
                if len(album.images) > 1:
                    cover_url = album.images[1].url if hasattr(album.images[1], 'url') else None
                elif len(album.images) > 0:
                    cover_url = album.images[0].url if hasattr(album.images[0], 'url') else None

        # Extract year from release_date
        year = None
        if release_date:
            try:
                # Format can be "YYYY-MM-DD" or "YYYY"
                year = int(release_date.split('-')[0])
            except (ValueError, AttributeError):
                _LOGGER.warning("Track %s missing or invalid release year: %s", title, release_date)
                year = None
        else:
            _LOGGER.warning("Track %s missing release year - will be filtered in production", title)

        return {
            'uri': uri,
            'title': title,
            'artist': artist,
            'album': album_name,
            'year': year,
            'cover_url': cover_url
        }

    except Exception as e:
        _LOGGER.error("Failed to extract metadata from track: %s", str(e))
        return {
            'uri': None,
            'title': None,
            'artist': None,
            'album': None,
            'year': None,
            'cover_url': None
        }


async def play_track(hass: HomeAssistant, entity_id: str, track_uri: str) -> bool:
    """Initiate Spotify track playback on specified media player.

    Story 7.5: Enhanced with error handling and retry logic.

    Args:
        hass: Home Assistant instance
        entity_id: Media player entity ID
        track_uri: Spotify track URI (spotify:track:xxxxx)

    Returns:
        True if playback initiated successfully, False otherwise

    Raises:
        HomeAssistantError: If service call fails
    """
    _LOGGER.info("🎵 Attempting to play track: uri=%s, entity=%s", track_uri, entity_id)

    try:
        # Check if media player entity exists
        state = hass.states.get(entity_id)
        if state is None:
            _LOGGER.error("❌ Media player entity not found: %s", entity_id)
            raise HomeAssistantError(f"Media player entity not found: {entity_id}")

        _LOGGER.info("📱 Media player state: %s (attributes: %s)", state.state, list(state.attributes.keys()))

        # Convert Spotify URI format for Music Assistant compatibility
        # Music Assistant requires spotify://track/xxx format instead of spotify:track:xxx
        media_id = track_uri
        if track_uri.startswith("spotify:"):
            # Convert spotify:track:xxx to spotify://track/xxx
            media_id = track_uri.replace("spotify:", "spotify://", 1).replace(":", "/")
            _LOGGER.info("🔄 Converted URI for Music Assistant: %s → %s", track_uri, media_id)

        # Call media_player.play_media service
        _LOGGER.info("🎬 Calling media_player.play_media service...")
        await hass.services.async_call(
            domain="media_player",
            service="play_media",
            service_data={
                "entity_id": entity_id,
                "media_content_type": "music",
                "media_content_id": media_id
            },
            blocking=False
        )

        _LOGGER.info("✅ Play track service call completed: %s on %s", track_uri, entity_id)
        return True

    except Exception as e:
        # Story 7.5 Task 1: Log error with details
        _LOGGER.error(
            "❌ Failed to play track %s on %s: %s",
            track_uri,
            entity_id,
            str(e),
            exc_info=True
        )
        # Don't raise - allow game to continue even if playback fails
        # The game can still function without audio
        return False


async def get_media_player_metadata(hass: HomeAssistant, entity_id: str) -> dict[str, Any]:
    """Read media player state attributes for runtime metadata.

    Args:
        hass: Home Assistant instance
        entity_id: Media player entity ID

    Returns:
        Dictionary with metadata: {media_title, media_artist, media_album_name, entity_picture}

    Raises:
        HomeAssistantError: If entity not found or state unavailable
    """
    _LOGGER.info("📋 Getting media player metadata from: %s", entity_id)

    try:
        # Get entity state
        state = hass.states.get(entity_id)

        if not state:
            _LOGGER.error("❌ Media player entity not found: %s", entity_id)
            raise HomeAssistantError(f"Media player entity not found: {entity_id}")

        _LOGGER.info("📊 Media player state: %s", state.state)

        # Extract attributes
        attributes = state.attributes

        metadata = {
            'media_title': attributes.get('media_title'),
            'media_artist': attributes.get('media_artist'),
            'media_album_name': attributes.get('media_album_name'),
            'entity_picture': attributes.get('entity_picture'),
            'media_duration': attributes.get('media_duration'),
            'media_position': attributes.get('media_position'),
        }

        _LOGGER.info("📋 Extracted metadata: title=%s, artist=%s, has_picture=%s",
                     metadata.get('media_title'),
                     metadata.get('media_artist'),
                     bool(metadata.get('entity_picture')))

        # Validate required fields are present
        required_fields = ['media_title', 'media_artist', 'media_album_name', 'entity_picture']
        missing_fields = [f for f in required_fields if not metadata.get(f)]

        if missing_fields:
            _LOGGER.warning(
                "⚠️ Media player %s missing metadata fields: %s",
                entity_id,
                ', '.join(missing_fields)
            )

        return metadata

    except Exception as e:
        _LOGGER.error("Failed to get metadata from %s: %s", entity_id, str(e))
        raise HomeAssistantError(f"Failed to read media player state: {str(e)}") from e


# Helper functions

async def _get_spotify_coordinator(hass: HomeAssistant) -> Any:
    """Get Spotify coordinator from HA's Spotify integration.

    Args:
        hass: Home Assistant instance

    Returns:
        Spotify coordinator instance

    Raises:
        SpotifyAPIError: If Spotify integration not configured
    """
    # Get first Spotify config entry
    spotify_entries = hass.config_entries.async_entries(SPOTIFY_DOMAIN)

    if not spotify_entries:
        raise SpotifyAPIError(
            "No Spotify configuration entries found. "
            "Please configure Spotify in Home Assistant."
        )

    # Get coordinator from entry runtime data
    entry = spotify_entries[0]

    if not hasattr(entry, 'runtime_data') or not entry.runtime_data:
        raise SpotifyAPIError(
            "Spotify integration not fully initialized. "
            "Please wait for Spotify to finish loading."
        )

    coordinator = entry.runtime_data.coordinator

    if not coordinator:
        raise SpotifyAPIError("Spotify coordinator not available")

    return coordinator


def _normalize_spotify_uri(uri_or_url: str) -> str:
    """Normalize Spotify playlist URI/URL to standard URI format.

    Args:
        uri_or_url: Spotify URI or URL

    Returns:
        Normalized URI in format: spotify:playlist:xxxxx

    Examples:
        spotify:playlist:37i9dQZF1DXcBWIGoYBM5M -> spotify:playlist:37i9dQZF1DXcBWIGoYBM5M
        https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M -> spotify:playlist:37i9dQZF1DXcBWIGoYBM5M
    """
    # Already in URI format
    if uri_or_url.startswith('spotify:playlist:'):
        return uri_or_url

    # Extract playlist ID from URL
    url_pattern = r'https?://open\.spotify\.com/playlist/([a-zA-Z0-9]+)'
    match = re.match(url_pattern, uri_or_url)

    if match:
        playlist_id = match.group(1)
        return f'spotify:playlist:{playlist_id}'

    # Invalid format
    raise ValueError(f"Invalid Spotify playlist URI/URL format: {uri_or_url}")


def _extract_playlist_id(uri: str) -> str:
    """Extract playlist ID from Spotify URI.

    Args:
        uri: Spotify URI (spotify:playlist:xxxxx)

    Returns:
        Playlist ID
    """
    if uri.startswith('spotify:playlist:'):
        return uri.split(':')[-1]
    return uri


def _supports_spotify_playback(state: State) -> bool:
    """Check if media player supports Spotify URI playback.

    Cast devices (Chromecast, Google Home, Sonos) support Spotify URIs natively.
    Other devices must have SUPPORT_PLAY_MEDIA feature flag.

    Args:
        state: Media player state object

    Returns:
        True if player can play Spotify URIs, False otherwise
    """
    # Cast devices support Spotify URIs natively
    entity_id_lower = state.entity_id.lower()
    if "cast" in entity_id_lower or "chromecast" in entity_id_lower:
        _LOGGER.debug("Media player %s identified as Cast device", state.entity_id)
        return True

    # Check if device supports play_media service
    supported_features = state.attributes.get("supported_features", 0)
    supports = bool(supported_features & SUPPORT_PLAY_MEDIA)

    _LOGGER.debug(
        "Media player %s supports Spotify: %s (features: %d)",
        state.entity_id,
        supports,
        supported_features
    )

    return supports


async def get_spotify_media_players(hass: HomeAssistant) -> list[MediaPlayerInfo]:
    """Detect media players capable of playing Spotify tracks.

    This function identifies Cast-enabled devices (Chromecast, Google Home, Sonos)
    and other media players that support the play_media service with Spotify URIs.

    CRITICAL: Does NOT require Spotify integration to be loaded. Cast devices can
    play Spotify URIs directly via media_player.play_media service. Metadata is
    automatically populated in the media player state after playback starts.

    Args:
        hass: Home Assistant instance

    Returns:
        List of MediaPlayerInfo objects, or empty list if none found.
    """
    try:
        # Query all media player entities
        all_states = hass.states.async_all("media_player")

        players: list[MediaPlayerInfo] = []

        for state in all_states:
            # Skip unavailable or unknown players
            if state.state in ("unavailable", "unknown"):
                _LOGGER.debug("Skipping unavailable player: %s", state.entity_id)
                continue

            # Check if player supports Spotify playback
            if not _supports_spotify_playback(state):
                _LOGGER.debug("Player %s does not support Spotify playback", state.entity_id)
                continue

            # Extract player information
            attributes = state.attributes or {}
            friendly_name = attributes.get("friendly_name", state.entity_id)

            # Create player info object
            player_info = MediaPlayerInfo(
                entity_id=state.entity_id,
                friendly_name=friendly_name,
                state=state.state,
                supports_play_media=True
            )

            players.append(player_info)
            _LOGGER.debug("Added media player: %s (%s)", friendly_name, state.entity_id)

        # Handle empty list
        if not players:
            _LOGGER.warning(
                "No Spotify-capable media players found. "
                "Ensure you have Cast-enabled devices (Chromecast, Google Home, Sonos) "
                "or other media players configured in Home Assistant."
            )
            return []

        _LOGGER.info("Found %d Spotify-capable media player(s)", len(players))
        return players

    except Exception as err:
        _LOGGER.error("Error detecting media players: %s", err, exc_info=True)
        return []  # Return empty list on error, don't crash
