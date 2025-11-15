"""Spotify media player service integration for Beatsy.

Story 7.3: Media player state detection and conflict handling.
Story 7.6: Media player state restoration after game ends.
Story 10.4: Error handling hardening with retry logic.

This module provides functions to query, save, and restore media player state
before/after game sessions, enabling restoration after game ends.

Architecture:
- Uses Home Assistant's state API (hass.states.get) to query media player
- No direct Spotify API calls - leverages HA's existing Spotify integration
- State stored in-memory in game_config.saved_player_state (ephemeral)
- Graceful degradation for offline/unavailable players
- Best-effort restoration - never blocks game end
- Story 10.4: Retry logic with exponential backoff for playback failures
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Any, Optional

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .game_state import MediaPlayerState

_LOGGER = logging.getLogger(__name__)


# ============================================================================
# Custom Exceptions
# ============================================================================


class PlaybackError(Exception):
    """Raised when track playback fails after all retry attempts."""

    pass


async def get_media_player_state(
    hass: HomeAssistant, entity_id: str
) -> Optional[MediaPlayerState]:
    """Query Home Assistant for current media player state.

    Story 7.3: Captures complete playback state including metadata, volume,
    and position for later restoration. Handles missing/incomplete attributes
    gracefully by setting Optional fields to None.

    Args:
        hass: The Home Assistant instance.
        entity_id: The media player entity ID to query (e.g., "media_player.living_room").

    Returns:
        MediaPlayerState object with all available fields, or None if player is unavailable.

    AC-1: Queries hass.states.get(entity_id) for current state
    AC-2: Extracts state attribute ("playing", "paused", "idle", "off", "unavailable")
    AC-3: Extracts attributes: source, media_title, media_artist, volume_level, media_position
    AC-4: Handles missing attributes gracefully (sets Optional fields to None)
    AC-5: Returns None if player is unavailable/offline
    AC-6: Comprehensive logging (INFO, WARNING, DEBUG)
    """
    _LOGGER.info("Checking media player state: %s", entity_id)

    # AC-1: Query HA state
    state_obj = hass.states.get(entity_id)

    # AC-5: Handle unavailable/offline player
    if state_obj is None:
        _LOGGER.warning(
            "Media player %s not found in Home Assistant (entity does not exist)",
            entity_id,
        )
        return None

    if state_obj.state == "unavailable":
        _LOGGER.info(
            "Media player %s is unavailable/offline (treating as idle, no conflict warning)",
            entity_id,
        )
        return None

    # AC-2: Extract state
    player_state = state_obj.state
    attributes = state_obj.attributes

    # AC-3: Extract attributes with graceful fallback for missing values
    # AC-4: Use .get() with None default for Optional fields
    source = attributes.get("source")
    media_title = attributes.get("media_title")
    media_artist = attributes.get("media_artist")
    volume_level = attributes.get("volume_level", 0.5)  # Default to 50% if not available
    position = attributes.get("media_position")

    # AC-6: DEBUG logging with captured state
    _LOGGER.debug(
        "Media player state captured: state=%s, source=%s, title=%s, artist=%s, volume=%.2f, position=%s",
        player_state,
        source,
        media_title,
        media_artist,
        volume_level,
        position,
    )

    # AC-4: Warn about missing features (but don't fail)
    missing_features = []
    if source is None:
        missing_features.append("source")
    if media_title is None:
        missing_features.append("media_title")
    if media_artist is None:
        missing_features.append("media_artist")
    if position is None:
        missing_features.append("media_position")

    if missing_features:
        _LOGGER.warning(
            "Media player %s does not support features: %s (will save partial state)",
            entity_id,
            ", ".join(missing_features),
        )

    # Create MediaPlayerState object
    media_player_state = MediaPlayerState(
        entity_id=entity_id,
        source=source,
        media_title=media_title,
        media_artist=media_artist,
        volume_level=volume_level,
        position=position,
        state=player_state,
        saved_at=datetime.now(),
    )

    return media_player_state


def should_warn_conflict(state: Optional[MediaPlayerState]) -> bool:
    """Determine if conflict warning should be shown to admin.

    Story 7.3: Conflict detection logic. Shows warning if player is actively
    playing or paused (user may want to resume). No warning for idle/off.

    Args:
        state: The MediaPlayerState object from get_media_player_state(), or None.

    Returns:
        True if conflict warning should be shown, False otherwise.

    AC-1: Return True if state is "playing" or "paused"
    AC-2: Return False if state is None (unavailable player)
    AC-3: Return False if state is "idle", "off", or any other value
    """
    if state is None:
        # AC-2: Unavailable player - no conflict
        return False

    # AC-1: Show warning for playing or paused states
    if state.state in ["playing", "paused"]:
        _LOGGER.info(
            "Media player %s is %s, showing conflict warning",
            state.entity_id,
            state.state,
        )
        return True

    # AC-3: Idle or off - no conflict
    _LOGGER.debug(
        "Media player %s is %s, no conflict warning needed",
        state.entity_id,
        state.state,
    )
    return False


def save_player_state(
    hass: HomeAssistant,
    state: MediaPlayerState,
    entry_id: Optional[str] = None,
) -> None:
    """Save media player state to game state for later restoration.

    Story 7.3: Stores MediaPlayerState in hass.data[DOMAIN][entry_id].saved_player_state.
    This is in-memory ephemeral storage - state persists only during active game session.

    Args:
        hass: The Home Assistant instance.
        state: The MediaPlayerState to save.
        entry_id: The config entry ID. If None, uses first entry.

    Side Effects:
        - Sets game_state.saved_player_state to provided MediaPlayerState
        - Logs INFO message with saved state details

    AC-1: Store state in hass.data[DOMAIN][entry_id].saved_player_state
    AC-2: Log INFO message with entity_id and media info
    """
    from .game_state import get_game_state

    game_state = get_game_state(hass, entry_id)

    # AC-1: Store state in game state object
    game_state.saved_player_state = state

    # AC-2: Log INFO with state details
    _LOGGER.info(
        "Saved player state: %s playing '%s' by '%s' (state=%s, volume=%.2f)",
        state.entity_id,
        state.media_title or "Unknown",
        state.media_artist or "Unknown",
        state.state,
        state.volume_level,
    )


async def safe_play_track(
    hass: HomeAssistant,
    entity_id: str,
    track_uri: str,
    retries: int = 3,
) -> dict[str, Any]:
    """Play track with retry logic and comprehensive error handling.

    Story 10.4: Implements retry logic with exponential backoff for playback failures.
    Provides user-friendly error messages and detailed logging for debugging.

    Args:
        hass: The Home Assistant instance.
        entity_id: The media player entity ID.
        track_uri: Spotify track URI to play.
        retries: Maximum number of retry attempts (default: 3).

    Returns:
        Dict with playback result: {success: bool, error: Optional[str], attempts: int}

    Raises:
        PlaybackError: If playback fails after all retry attempts.

    Example:
        >>> result = await safe_play_track(hass, "media_player.living_room",
        ...     "spotify:track:123", retries=3)
        >>> if result["success"]:
        ...     print("Track playing!")
    """
    delay = 1.0  # Initial delay in seconds
    last_exception = None

    for attempt in range(retries):
        try:
            _LOGGER.info(
                "Playing track on %s (attempt %d/%d): %s",
                entity_id,
                attempt + 1,
                retries,
                track_uri,
            )

            # Call media_player.play_media service
            await hass.services.async_call(
                domain="media_player",
                service="play_media",
                service_data={
                    "entity_id": entity_id,
                    "media_content_id": track_uri,
                    "media_content_type": "music",
                },
                blocking=True,
            )

            # Success! Log and return
            _LOGGER.info(
                "Track playback started successfully on %s (attempt %d/%d)",
                entity_id,
                attempt + 1,
                retries,
            )

            return {"success": True, "error": None, "attempts": attempt + 1}

        except HomeAssistantError as e:
            last_exception = e

            # Log warning for retry attempts, error for final failure
            if attempt < retries - 1:
                _LOGGER.warning(
                    "Playback failed on %s (attempt %d/%d), retrying in %.1fs: %s",
                    entity_id,
                    attempt + 1,
                    retries,
                    delay,
                    str(e),
                )

                # Wait before retrying with exponential backoff
                await asyncio.sleep(delay)
                delay *= 2  # Exponential backoff: 1s, 2s, 4s

            else:
                # Final attempt failed
                _LOGGER.error(
                    "Playback failed on %s after %d attempts: %s",
                    entity_id,
                    retries,
                    str(e),
                    exc_info=True,
                )

        except Exception as e:
            last_exception = e

            # Unexpected error - log and fail immediately
            _LOGGER.error(
                "Unexpected error during playback on %s: %s",
                entity_id,
                str(e),
                exc_info=True,
            )

            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "attempts": attempt + 1,
            }

    # All retries exhausted
    error_msg = f"Playback failed after {retries} attempts: {str(last_exception)}"

    return {"success": False, "error": error_msg, "attempts": retries}


async def restore_player_state(
    hass: HomeAssistant,
    saved_state: MediaPlayerState,
    entry_id: Optional[str] = None,
) -> dict[str, Any]:
    """Restore media player to previous state (best-effort).

    Story 7.6: Restores media player state after game ends. Implements best-effort
    restoration - each step is independent, failures are logged but don't prevent
    other restoration steps or block game end.

    Args:
        hass: The Home Assistant instance.
        saved_state: The MediaPlayerState to restore from Story 7.3.
        entry_id: The config entry ID. If None, uses first entry.

    Returns:
        Dict with restoration summary: {success: bool, errors: [str]}
        - success: True if all steps succeeded, False if any step failed
        - errors: List of error messages for failed steps

    Side Effects:
        - Calls HA services: volume_set, select_source, media_seek, media_play
        - Logs INFO for each successful step
        - Logs WARNING for each failed step

    AC-1: Restore volume, source, position, and playback state
    AC-2: Best-effort approach - log errors but never raise exceptions
    AC-3: Return early if no saved state (leave player idle)
    """
    # AC-3: Check if saved state exists and is valid
    if not saved_state or not saved_state.is_valid():
        _LOGGER.info("No valid state to restore")
        return {"success": True, "errors": []}

    _LOGGER.info("Restoring media player state: %s", saved_state.entity_id)

    errors = []

    # Step 1: Restore volume
    try:
        await _restore_volume(hass, saved_state.entity_id, saved_state.volume_level)
        _LOGGER.info(
            "Restored volume for %s: %.2f",
            saved_state.entity_id,
            saved_state.volume_level,
        )
    except Exception as e:
        error_msg = f"Volume restore failed: {e}"
        errors.append(error_msg)
        _LOGGER.warning(
            "Failed to restore volume for %s: %s",
            saved_state.entity_id,
            str(e),
        )

    # Step 2: Restore source (if available)
    if saved_state.source:
        try:
            # Check if player supports source selection
            if _supports_select_source(hass, saved_state.entity_id):
                await _restore_source(hass, saved_state.entity_id, saved_state.source)
                _LOGGER.info(
                    "Restored source for %s: %s",
                    saved_state.entity_id,
                    saved_state.source,
                )
            else:
                _LOGGER.info(
                    "Media player %s does not support source selection, skipping",
                    saved_state.entity_id,
                )
        except Exception as e:
            error_msg = f"Source restore failed: {e}"
            errors.append(error_msg)
            _LOGGER.warning(
                "Failed to restore source for %s: %s",
                saved_state.entity_id,
                str(e),
            )

    # Step 3: Resume playback if was playing
    if saved_state.state == "playing":
        try:
            # Step 3a: Restore position if available and supported
            if saved_state.position is not None and _supports_seek(hass, saved_state.entity_id):
                await _restore_position(hass, saved_state.entity_id, saved_state.position)
                _LOGGER.info(
                    "Restored position for %s: %.1fs",
                    saved_state.entity_id,
                    saved_state.position,
                )
            elif saved_state.position is not None:
                _LOGGER.info(
                    "Media player %s does not support seek, skipping position restore",
                    saved_state.entity_id,
                )

            # Step 3b: Resume playback
            await _resume_playback(hass, saved_state.entity_id)
            _LOGGER.info("Resumed playback on %s", saved_state.entity_id)

        except Exception as e:
            error_msg = f"Playback resume failed: {e}"
            errors.append(error_msg)
            _LOGGER.warning(
                "Failed to resume playback on %s: %s",
                saved_state.entity_id,
                str(e),
            )

    # Calculate success
    success = len(errors) == 0

    # Log completion
    if success:
        _LOGGER.info(
            "Restoration complete: %s (all steps successful)",
            saved_state.entity_id,
        )
    else:
        _LOGGER.warning(
            "Restoration complete with %d error(s): %s",
            len(errors),
            saved_state.entity_id,
        )

    return {"success": success, "errors": errors}


# Helper functions for restoration


def _supports_seek(hass: HomeAssistant, entity_id: str) -> bool:
    """Check if media player supports position seeking.

    Args:
        hass: The Home Assistant instance.
        entity_id: The media player entity ID.

    Returns:
        True if player supports SEEK feature, False otherwise.
    """
    state = hass.states.get(entity_id)
    if not state:
        return False

    supported_features = state.attributes.get("supported_features", 0)
    # MediaPlayerEntityFeature.SEEK = 1024
    SEEK_FEATURE = 1024
    return (supported_features & SEEK_FEATURE) != 0


def _supports_select_source(hass: HomeAssistant, entity_id: str) -> bool:
    """Check if media player supports source selection.

    Args:
        hass: The Home Assistant instance.
        entity_id: The media player entity ID.

    Returns:
        True if player supports SELECT_SOURCE feature, False otherwise.
    """
    state = hass.states.get(entity_id)
    if not state:
        return False

    supported_features = state.attributes.get("supported_features", 0)
    # MediaPlayerEntityFeature.SELECT_SOURCE = 128
    SELECT_SOURCE_FEATURE = 128
    return (supported_features & SELECT_SOURCE_FEATURE) != 0


async def _restore_volume(hass: HomeAssistant, entity_id: str, volume_level: float) -> None:
    """Restore volume level on media player.

    Args:
        hass: The Home Assistant instance.
        entity_id: The media player entity ID.
        volume_level: Volume level (0.0-1.0).

    Raises:
        HomeAssistantError: If service call fails.
    """
    # Validate volume_level is in range
    if not (0.0 <= volume_level <= 1.0):
        raise ValueError(f"Volume level must be 0.0-1.0, got {volume_level}")

    await hass.services.async_call(
        domain="media_player",
        service="volume_set",
        service_data={
            "entity_id": entity_id,
            "volume_level": volume_level,
        },
        blocking=False,
    )


async def _restore_source(hass: HomeAssistant, entity_id: str, source: str) -> None:
    """Restore playback source on media player.

    Args:
        hass: The Home Assistant instance.
        entity_id: The media player entity ID.
        source: Source name (e.g., "Spotify").

    Raises:
        HomeAssistantError: If service call fails.
    """
    await hass.services.async_call(
        domain="media_player",
        service="select_source",
        service_data={
            "entity_id": entity_id,
            "source": source,
        },
        blocking=False,
    )


async def _restore_position(hass: HomeAssistant, entity_id: str, position: float) -> None:
    """Restore playback position on media player.

    Args:
        hass: The Home Assistant instance.
        entity_id: The media player entity ID.
        position: Position in seconds.

    Raises:
        HomeAssistantError: If service call fails.
    """
    await hass.services.async_call(
        domain="media_player",
        service="media_seek",
        service_data={
            "entity_id": entity_id,
            "seek_position": position,
        },
        blocking=False,
    )


async def _resume_playback(hass: HomeAssistant, entity_id: str) -> None:
    """Resume playback on media player.

    Args:
        hass: The Home Assistant instance.
        entity_id: The media player entity ID.

    Raises:
        HomeAssistantError: If service call fails.
    """
    await hass.services.async_call(
        domain="media_player",
        service="media_play",
        service_data={
            "entity_id": entity_id,
        },
        blocking=False,
    )
