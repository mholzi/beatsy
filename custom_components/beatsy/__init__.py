"""Beatsy custom component for Home Assistant.

This component provides a music guessing game integration that works with Spotify.
Uses modern config entry pattern for Home Assistant 2025.
"""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components import websocket_api as ha_websocket_api
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .game_state import init_game_state, load_config
from .http_view import (
    BeatsyTestView,
    BeatsyAdminView,
    BeatsyPlayerView,
    BeatsyAPIView,
)
from .websocket_handler import BeatsyWebSocketView, close_all_connections
from .spotify_helper import (
    fetch_playlist_tracks,
    extract_track_metadata,
    play_track,
    get_media_player_metadata,
    get_spotify_media_players,
)
from .websocket_api import (
    handle_join_game,
    handle_submit_guess,
    handle_place_bet,
    handle_start_game,
    handle_next_song,
)

_LOGGER = logging.getLogger(__name__)

# Empty platforms list - will be populated in later stories (e.g., ['sensor', 'switch'])
PLATFORMS: list[str] = []


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Beatsy from a config entry.

    Args:
        hass: The Home Assistant instance.
        entry: The config entry being set up.

    Returns:
        True if setup was successful.
    """
    # Load configuration from config entry (Story 2.7)
    entry_config = entry.data
    timer_duration = entry_config.get("timer_duration", 30)
    year_range_min = entry_config.get("year_range_min", 1950)
    year_range_max = entry_config.get("year_range_max", 2024)

    _LOGGER.info(
        "Beatsy integration loaded from config entry "
        "(timer=%ds, years=%d-%d)",
        timer_duration, year_range_min, year_range_max
    )

    # Initialize game state using BeatsyGameState dataclass (Story 2.3)
    # This provides type-safe, structured state management
    state = init_game_state(hass, entry.entry_id)

    # Apply config entry values to game config
    state.game_config["timer_duration"] = timer_duration
    state.game_config["year_range_min"] = year_range_min
    state.game_config["year_range_max"] = year_range_max

    # Load persisted config from storage (if exists) - may override entry config
    persisted_config = await load_config(hass, entry.entry_id)
    if persisted_config:
        state.game_config.update(persisted_config)
        _LOGGER.debug("Loaded persisted config for entry %s", entry.entry_id)

    # Store Spotify helper functions reference in state
    state.spotify = {
        "fetch_playlist_tracks": fetch_playlist_tracks,
        "extract_track_metadata": extract_track_metadata,
        "play_track": play_track,
        "get_media_player_metadata": get_media_player_metadata,
        "get_media_players": get_spotify_media_players,
    }

    _LOGGER.info("Beatsy integration loaded")
    _LOGGER.info("Beatsy: Spotify helper loaded")

    # Detect and validate Spotify-capable media players
    players = await get_spotify_media_players(hass)
    _LOGGER.info("Beatsy initialized with %d media player(s) available", len(players))

    # Check if Spotify integration is configured (optional dependency)
    spotify_entries = hass.config_entries.async_entries("spotify")
    if not spotify_entries:
        _LOGGER.info(
            "Spotify integration not configured. "
            "Beatsy will work, but Spotify features require configuring the Spotify integration first."
        )
    else:
        _LOGGER.info("Spotify integration detected - Full Spotify features available")

    # Register HTTP views and WebSocket commands (global, one-time registration)
    # Use a simple flag in hass.data to track if we've registered them
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    if not hass.data[DOMAIN].get("_http_views_registered", False):
        try:
            hass.http.register_view(BeatsyTestView())
            hass.http.register_view(BeatsyAdminView())
            hass.http.register_view(BeatsyPlayerView())
            hass.http.register_view(BeatsyAPIView())
            hass.http.register_view(BeatsyWebSocketView(hass))
            hass.data[DOMAIN]["_http_views_registered"] = True
            _LOGGER.info(
                "HTTP routes registered: /api/beatsy/test.html, /beatsy/admin, "
                "/api/beatsy/player, /api/beatsy/api/*, /api/beatsy/ws"
            )
        except Exception as e:
            _LOGGER.warning("Failed to register HTTP routes (may already exist): %s", str(e))
            # Don't return False - let it continue even if views fail to register
    else:
        _LOGGER.debug("HTTP views already registered, skipping")

    if not hass.data[DOMAIN].get("_ws_commands_registered", False):
        try:
            ha_websocket_api.async_register_command(hass, handle_join_game)
            ha_websocket_api.async_register_command(hass, handle_submit_guess)
            ha_websocket_api.async_register_command(hass, handle_place_bet)
            ha_websocket_api.async_register_command(hass, handle_start_game)
            ha_websocket_api.async_register_command(hass, handle_next_song)
            hass.data[DOMAIN]["_ws_commands_registered"] = True
            _LOGGER.info(
                "WebSocket commands registered: join_game, submit_guess, place_bet, start_game, next_song"
            )
        except Exception as e:
            _LOGGER.warning("Failed to register WebSocket commands (may already exist): %s", str(e))
            # Don't return False - let it continue even if commands fail to register
    else:
        _LOGGER.debug("WebSocket commands already registered, skipping")

    # Register test service for Spotify playlist fetching (POC validation)
    async def test_fetch_playlist(call):
        """Test service to fetch Spotify playlist tracks."""
        playlist_uri = call.data.get("playlist_uri")

        if not playlist_uri:
            _LOGGER.error("No playlist_uri provided in service call")
            return

        try:
            _LOGGER.info("Testing playlist fetch for: %s", playlist_uri)

            # Fetch playlist tracks
            tracks = await fetch_playlist_tracks(hass, playlist_uri)
            _LOGGER.info("✅ Fetched %d tracks from playlist", len(tracks))

            # Extract metadata from first 3 tracks as sample
            tracks_with_year = 0
            tracks_without_year = 0

            for i, track in enumerate(tracks[:3], 1):
                metadata = extract_track_metadata(track)
                _LOGGER.info(
                    "Track %d: %s - %s (%s) [Album: %s]",
                    i,
                    metadata.get("title"),
                    metadata.get("artist"),
                    metadata.get("year") or "NO YEAR",
                    metadata.get("album"),
                )

                if metadata.get("year"):
                    tracks_with_year += 1
                else:
                    tracks_without_year += 1

            # Count tracks with/without year data
            for track in tracks[3:]:
                metadata = extract_track_metadata(track)
                if metadata.get("year"):
                    tracks_with_year += 1
                else:
                    tracks_without_year += 1

            _LOGGER.info("=" * 60)
            _LOGGER.info("📊 PLAYLIST ANALYSIS COMPLETE")
            _LOGGER.info("=" * 60)
            _LOGGER.info("Total tracks: %d", len(tracks))
            _LOGGER.info(
                "Tracks with year: %d (%.1f%%)",
                tracks_with_year,
                (tracks_with_year / len(tracks) * 100) if tracks else 0,
            )
            _LOGGER.info(
                "Tracks without year: %d (%.1f%%)",
                tracks_without_year,
                (tracks_without_year / len(tracks) * 100) if tracks else 0,
            )
            _LOGGER.info("=" * 60)

        except Exception as e:
            _LOGGER.error("❌ Failed to fetch playlist: %s", str(e), exc_info=True)

    hass.services.async_register(DOMAIN, "test_fetch_playlist", test_fetch_playlist)
    _LOGGER.info("Beatsy test service registered: beatsy.test_fetch_playlist")

    # Forward to platforms (empty list for now, platforms added in later stories)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register reload listener for config changes (Story 2.7 - AC-6)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    _LOGGER.debug("Config entry reload listener registered")

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a Beatsy config entry.

    Args:
        hass: The Home Assistant instance.
        entry: The config entry being unloaded.

    Returns:
        True if unload was successful.
    """
    # Unload platforms first
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        # Get and remove entry data (now a BeatsyGameState object)
        # Defensive: Check if DOMAIN exists and has our entry_id
        if DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN]:
            state = hass.data[DOMAIN].pop(entry.entry_id)

            # Close all WebSocket connections (Story 2.6)
            # Handle both dict (legacy) and BeatsyGameState (current)
            try:
                if hasattr(state, "websocket_connections"):
                    websocket_connections = state.websocket_connections
                else:
                    websocket_connections = state.get("websocket_connections", {})

                for connection_id, conn_info in list(websocket_connections.items()):
                    try:
                        connection = conn_info.get("connection")
                        if connection and hasattr(connection, "close"):
                            await connection.close()
                        _LOGGER.debug(f"Closed WebSocket connection: {connection_id}")
                    except Exception as e:
                        _LOGGER.warning(f"Error closing connection {connection_id}: {e}")

                # Clear connection tracking
                websocket_connections.clear()
            except Exception as e:
                _LOGGER.warning(f"Error during WebSocket cleanup: {e}")
        else:
            _LOGGER.debug(f"Entry {entry.entry_id} not found in hass.data during unload")

        # Note: HTTP views are global and shared across all entries
        # They will be unregistered when HA shuts down
        # Future enhancement: Track views per entry for proper cleanup

    _LOGGER.info("Beatsy integration unloaded (WebSocket connections closed)")
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload a Beatsy config entry.

    Args:
        hass: The Home Assistant instance.
        entry: The config entry being reloaded.
    """
    _LOGGER.info("Starting reload for entry %s", entry.entry_id)
    try:
        unload_success = await async_unload_entry(hass, entry)
        if not unload_success:
            _LOGGER.error("Failed to unload entry during reload")
            return

        _LOGGER.info("Unload successful, setting up entry again")
        setup_success = await async_setup_entry(hass, entry)
        if not setup_success:
            _LOGGER.error("Failed to setup entry during reload")
            return

        _LOGGER.info("Beatsy integration reloaded successfully")
    except Exception as e:
        _LOGGER.error("Error during reload: %s", str(e), exc_info=True)
        raise
