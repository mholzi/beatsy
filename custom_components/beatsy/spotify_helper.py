"""Spotify integration helper for Beatsy.

This module provides wrapper functions to interact with Home Assistant's
Spotify integration for fetching playlists, extracting metadata, and
controlling playback.

CRITICAL: Cast-enabled devices (Chromecast, Google Home, Sonos) can play
Spotify URIs directly via media_player.play_media service WITHOUT requiring
the Spotify integration to be loaded. Metadata is automatically populated
after playback starts.
"""
import logging
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


async def fetch_playlist_tracks(hass: HomeAssistant, playlist_uri: str) -> list[dict[str, Any]]:
    """Fetch all tracks from a Spotify playlist via HA's Spotify integration.

    Args:
        hass: Home Assistant instance
        playlist_uri: Spotify playlist URI (spotify:playlist:xxx or https://...)

    Returns:
        List of track dictionaries with Spotify API data

    Raises:
        HomeAssistantError: If Spotify integration not configured or playlist fetch fails
    """
    # Normalize URI format
    normalized_uri = _normalize_spotify_uri(playlist_uri)

    # Get Spotify integration coordinator
    coordinator = await _get_spotify_coordinator(hass)

    try:
        # Fetch playlist data via coordinator client
        playlist = await coordinator.client.get_playlist(normalized_uri)

        if not playlist or not hasattr(playlist, 'tracks'):
            raise HomeAssistantError(f"Invalid playlist data for URI: {normalized_uri}")

        # Extract track list from playlist
        tracks = []
        if hasattr(playlist.tracks, 'items'):
            for item in playlist.tracks.items:
                if item and hasattr(item, 'track') and item.track:
                    tracks.append(item.track)

        playlist_id = _extract_playlist_id(normalized_uri)
        _LOGGER.info("Beatsy: Fetched %d tracks from playlist %s", len(tracks), playlist_id)

        return tracks

    except Exception as e:
        _LOGGER.error("Failed to fetch playlist %s: %s", normalized_uri, str(e))
        raise HomeAssistantError(f"Failed to fetch playlist: {str(e)}") from e


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

    Args:
        hass: Home Assistant instance
        entity_id: Media player entity ID
        track_uri: Spotify track URI (spotify:track:xxxxx)

    Returns:
        True if playback initiated successfully, False otherwise

    Raises:
        HomeAssistantError: If service call fails
    """
    try:
        # Call media_player.play_media service
        await hass.services.async_call(
            domain="media_player",
            service="play_media",
            service_data={
                "entity_id": entity_id,
                "media_content_type": "music",
                "media_content_id": track_uri
            },
            blocking=False
        )

        _LOGGER.info("Beatsy: Playing track %s on %s", track_uri, entity_id)
        return True

    except Exception as e:
        _LOGGER.error("Failed to play track %s on %s: %s", track_uri, entity_id, str(e))
        raise HomeAssistantError(f"Failed to initiate playback: {str(e)}") from e


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
    try:
        # Get entity state
        state = hass.states.get(entity_id)

        if not state:
            raise HomeAssistantError(f"Media player entity not found: {entity_id}")

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

        # Validate required fields are present
        required_fields = ['media_title', 'media_artist', 'media_album_name', 'entity_picture']
        missing_fields = [f for f in required_fields if not metadata.get(f)]

        if missing_fields:
            _LOGGER.warning(
                "Media player %s missing metadata fields: %s",
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
        HomeAssistantError: If Spotify integration not configured
    """
    # Get first Spotify config entry
    spotify_entries = hass.config_entries.async_entries(SPOTIFY_DOMAIN)

    if not spotify_entries:
        raise HomeAssistantError(
            "No Spotify configuration entries found. "
            "Please configure Spotify in Home Assistant."
        )

    # Get coordinator from entry runtime data
    entry = spotify_entries[0]

    if not hasattr(entry, 'runtime_data') or not entry.runtime_data:
        raise HomeAssistantError(
            "Spotify integration not fully initialized. "
            "Please wait for Spotify to finish loading."
        )

    coordinator = entry.runtime_data.coordinator

    if not coordinator:
        raise HomeAssistantError("Spotify coordinator not available")

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
