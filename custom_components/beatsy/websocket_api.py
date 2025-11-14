"""WebSocket command registration for Beatsy real-time gameplay.

This module provides WebSocket command handlers for:
- Player actions: join_game, submit_guess, place_bet
- Admin actions: start_game, next_song
- Broadcast infrastructure: broadcast_event()

All commands follow HA WebSocket API conventions:
- Commands registered via websocket_api.async_register_command()
- Input validation via voluptuous schemas
- Commands use @callback decorator for synchronous execution
- Errors sent via connection.send_error()
- Success responses via connection.send_result()

Connection tracking:
- Connections stored in hass.data[DOMAIN]["websocket_connections"]
- Metadata: connection_id, player_name, connected_at, last_ping
- Automatic cleanup on disconnect or broadcast failure

Epic 2 Implementation:
- All commands have basic structure
- Admin commands have placeholders for Epic 3-5 logic
- Broadcast infrastructure ready for real-time events
"""

from __future__ import annotations

import logging
import time
import uuid
from typing import TYPE_CHECKING

import voluptuous as vol
from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN
from .game_state import (
    PlaylistExhaustedError,
    add_guess,
    add_player,
    find_player_by_session,
    get_current_round,
    get_players,
    initialize_game,
    select_random_song,
    update_bet,
)

if TYPE_CHECKING:
    from homeassistant.components.websocket_api import ActiveConnection

_LOGGER = logging.getLogger(__name__)

# Command type constants
WS_TYPE_JOIN_GAME = "beatsy/join_game"
WS_TYPE_RECONNECT = "beatsy/reconnect"  # Story 4.4
WS_TYPE_SUBMIT_GUESS = "beatsy/submit_guess"
WS_TYPE_PLACE_BET = "beatsy/place_bet"
WS_TYPE_START_GAME = "beatsy/start_game"
WS_TYPE_NEXT_SONG = "beatsy/next_song"

# Command schemas with voluptuous validation (HA 2025 format)
SCHEMA_JOIN_GAME = {
    vol.Required("type"): WS_TYPE_JOIN_GAME,
    vol.Required("player_name"): vol.All(str, vol.Length(min=1, max=20)),
    vol.Optional("game_id"): str,  # Future multi-game support
}

SCHEMA_RECONNECT = {
    vol.Required("type"): WS_TYPE_RECONNECT,
    vol.Required("session_id"): str,
    vol.Required("player_name"): vol.All(str, vol.Length(min=1, max=20)),
}

SCHEMA_SUBMIT_GUESS = {
    vol.Required("type"): WS_TYPE_SUBMIT_GUESS,
    vol.Required("player_name"): vol.All(str, vol.Length(min=1, max=20)),
    vol.Required("year_guess"): vol.All(int, vol.Range(min=1950, max=2050)),
    vol.Required("bet_placed"): bool,
}

SCHEMA_PLACE_BET = {
    vol.Required("type"): WS_TYPE_PLACE_BET,
    vol.Required("player_name"): vol.All(str, vol.Length(min=1, max=20)),
    vol.Required("bet"): bool,
}

SCHEMA_START_GAME = {
    vol.Required("type"): WS_TYPE_START_GAME,
    vol.Required("config"): dict,  # Game configuration
}

SCHEMA_NEXT_SONG = {
    vol.Required("type"): WS_TYPE_NEXT_SONG,
}


def find_unique_name(hass: HomeAssistant, requested_name: str) -> str:
    """Find unique player name, appending (N) if duplicate exists.

    Implements case-insensitive, whitespace-normalized duplicate detection.
    Preserves original capitalization in result.

    Algorithm:
    1. Normalize: strip whitespace, lowercase for comparison
    2. Check if normalized name exists in players list (case-insensitive)
    3. If unique: return original name (preserve capitalization)
    4. If duplicate: try " (2)", " (3)", etc. until unique
    5. Return adjusted name with original capitalization + suffix

    Args:
        hass: Home Assistant instance
        requested_name: Name as submitted by player

    Returns:
        Unique player name (original or with " (N)" suffix)
    """
    # Normalize name: strip whitespace, lowercase for comparison
    base_name = requested_name.strip()
    normalized = base_name.lower()

    # Get existing players
    players = get_players(hass)
    existing_names = {p.name.lower() for p in players}

    # Check if name already exists
    if normalized not in existing_names:
        return base_name  # No duplicate, return as-is

    # Find next available number
    counter = 2
    while True:
        candidate = f"{base_name} ({counter})"
        if candidate.lower() not in existing_names:
            return candidate
        counter += 1


@callback
@websocket_api.websocket_command(SCHEMA_JOIN_GAME)
def handle_join_game(
    hass: HomeAssistant,
    connection: ActiveConnection,
    msg: dict,
) -> None:
    """Handle join_game command.

    Registers a new player and tracks WebSocket connection.

    Args:
        hass: Home Assistant instance
        connection: WebSocket connection
        msg: Command message with player_name
    """
    try:
        requested_name = msg["player_name"].strip()
        game_id = msg.get("game_id")  # Optional, future use

        # Validate non-empty name
        if not requested_name or not requested_name.strip():
            connection.send_error(
                msg["id"], "invalid_name", "Player name cannot be empty"
            )
            return

        # Find unique name (handles duplicates automatically)
        unique_name = find_unique_name(hass, requested_name)
        name_adjusted = unique_name != requested_name

        _LOGGER.info(
            f"Player '{requested_name}' joining game"
            + (f" as '{unique_name}'" if name_adjusted else "")
        )

        # Add player to game state
        session_id = str(uuid.uuid4())
        add_player(
            hass,
            player_name=unique_name,
            session_id=session_id,
            is_admin=False,
            original_name=requested_name,
        )

        # Track WebSocket connection
        connection_id = str(uuid.uuid4())

        # Get the first entry's state for connection tracking
        entries = list(hass.data[DOMAIN].values())
        if entries:
            state = entries[0]
            if "websocket_connections" not in state:
                state["websocket_connections"] = {}

            state["websocket_connections"][connection_id] = {
                "player_name": unique_name,
                "connected_at": time.time(),
                "last_ping": time.time(),
                "connection": connection,
            }

        # Get all players for lobby initialization (Story 4.3 Task 4)
        all_players = get_players(hass)
        players_list = [
            {"name": p.name, "joined_at": p.joined_at}
            for p in sorted(all_players, key=lambda x: x.joined_at)
        ]

        # Send success response
        connection.send_result(
            msg["id"],
            {
                "success": True,
                "player_name": unique_name,
                "original_name": requested_name,
                "name_adjusted": name_adjusted,
                "session_id": session_id,
                "connection_id": connection_id,
                "players": players_list,  # Story 4.3: Full player list for lobby
            },
        )

        # Broadcast player_joined event to all clients (except joining player)
        # Story 4.3: Exclude joining player since they already have full list
        hass.async_create_task(
            broadcast_event(
                hass,
                "player_joined",
                {
                    "player_name": unique_name,
                    "total_players": len(get_players(hass)),
                },
                exclude_connection_id=connection_id,
            )
        )

    except ValueError as e:
        _LOGGER.warning(f"Validation error in join_game: {e}")
        connection.send_error(msg["id"], "validation_error", str(e))
    except Exception as e:
        _LOGGER.error(f"Error in join_game: {e}", exc_info=True)
        connection.send_error(msg["id"], "internal_error", "Failed to join game")


@callback
@websocket_api.websocket_command(SCHEMA_RECONNECT)
def handle_reconnect(
    hass: HomeAssistant,
    connection: ActiveConnection,
    msg: dict,
) -> None:
    """Handle reconnect command (Story 4.4).

    Reconnects a player using their session_id without losing their
    identity, score, and game progress.

    Args:
        hass: Home Assistant instance
        connection: WebSocket connection
        msg: Command message with session_id and player_name
    """
    try:
        session_id = msg["session_id"]
        player_name = msg["player_name"]

        _LOGGER.info(f"Player '{player_name}' attempting reconnection (session: {session_id})")

        # Find player by session_id
        player = find_player_by_session(hass, session_id)

        if player is None:
            _LOGGER.warning(f"Reconnection failed: session {session_id} not found")
            connection.send_result(
                msg["id"],
                {
                    "success": False,
                    "reason": "session_not_found",
                },
            )
            return

        # Check session expiration (24 hours = 86400 seconds)
        current_time = time.time()
        session_age = current_time - player.joined_at

        if session_age > 86400:  # 24 hours
            _LOGGER.warning(
                f"Reconnection failed: session {session_id} expired "
                f"(age: {session_age/3600:.1f}h)"
            )
            connection.send_result(
                msg["id"],
                {
                    "success": False,
                    "reason": "session_expired",
                },
            )
            return

        # Update player connection status
        player.connected = True
        player.last_activity = current_time

        _LOGGER.info(
            f"Player '{player.name}' reconnected successfully "
            f"(score: {player.score}, session age: {session_age/60:.1f}m)"
        )

        # Track WebSocket connection
        connection_id = str(uuid.uuid4())

        # Get the first entry's state for connection tracking
        entries = list(hass.data[DOMAIN].values())
        if entries:
            state = entries[0]
            if "websocket_connections" not in state:
                state["websocket_connections"] = {}

            state["websocket_connections"][connection_id] = {
                "player_name": player.name,
                "connected_at": current_time,
                "last_ping": current_time,
                "connection": connection,
            }

        # Determine current game status
        current_round = get_current_round(hass)
        all_players = get_players(hass)

        game_status = "lobby"  # Default to lobby
        if current_round and current_round.status == "active":
            game_status = "active"
        elif current_round and current_round.status == "ended":
            game_status = "results"

        # Build game state response
        game_state = {
            "status": game_status,
            "players": [p.name for p in sorted(all_players, key=lambda x: x.joined_at)],
        }

        # Add current round info if active
        if current_round:
            game_state["current_round"] = {
                "round_number": current_round.round_number,
                "track_name": current_round.track_name,
                "track_artist": current_round.track_artist,
                "status": current_round.status,
                "timer_started_at": current_round.timer_started_at,
                "started_at": current_round.started_at,
                "guesses": {
                    name: {
                        "submitted": True,
                        "bet": guess_data.get("bet", False),
                    }
                    for name, guess_data in current_round.guesses.items()
                },
            }

        # Send success response
        connection.send_result(
            msg["id"],
            {
                "success": True,
                "player": {
                    "name": player.name,
                    "score": player.score,
                    "session_id": player.session_id,
                },
                "game_state": game_state,
            },
        )

    except ValueError as e:
        _LOGGER.warning(f"Validation error in reconnect: {e}")
        connection.send_error(msg["id"], "validation_error", str(e))
    except Exception as e:
        _LOGGER.error(f"Error in reconnect: {e}", exc_info=True)
        connection.send_error(msg["id"], "internal_error", "Failed to reconnect")


@callback
@websocket_api.websocket_command(SCHEMA_SUBMIT_GUESS)
def handle_submit_guess(
    hass: HomeAssistant,
    connection: ActiveConnection,
    msg: dict,
) -> None:
    """Handle submit_guess command.

    Records player's year guess and bet status for current round.

    Args:
        hass: Home Assistant instance
        connection: WebSocket connection
        msg: Command message with player_name, year_guess, bet_placed
    """
    try:
        player_name = msg["player_name"]
        year_guess = msg["year_guess"]
        bet_placed = msg["bet_placed"]

        _LOGGER.debug(
            f"Player '{player_name}' submitting guess: {year_guess}, bet: {bet_placed}"
        )

        # Verify round is active
        current_round = get_current_round(hass)
        if not current_round or current_round.get("status") != "active":
            connection.send_error(
                msg["id"], "no_active_round", "No active round to submit guess"
            )
            return

        # Add guess to round state
        add_guess(hass, player_name, year_guess, bet_placed)

        # Send success response
        connection.send_result(
            msg["id"],
            {
                "success": True,
                "guess_recorded": True,
            },
        )

        # Broadcast guess_submitted event
        hass.async_create_task(
            broadcast_event(
                hass,
                "guess_submitted",
                {
                    "player_name": player_name,
                    "bet_placed": bet_placed,  # Don't reveal actual guess
                    "total_guesses": len(current_round.get("guesses", {})),
                },
            )
        )

    except ValueError as e:
        _LOGGER.warning(f"Validation error in submit_guess: {e}")
        connection.send_error(msg["id"], "validation_error", str(e))
    except Exception as e:
        _LOGGER.error(f"Error in submit_guess: {e}", exc_info=True)
        connection.send_error(msg["id"], "internal_error", "Failed to submit guess")


@callback
@websocket_api.websocket_command(SCHEMA_PLACE_BET)
def handle_place_bet(
    hass: HomeAssistant,
    connection: ActiveConnection,
    msg: dict,
) -> None:
    """Handle place_bet command.

    Updates player's bet status for current round.

    Args:
        hass: Home Assistant instance
        connection: WebSocket connection
        msg: Command message with player_name, bet
    """
    try:
        player_name = msg["player_name"]
        bet = msg["bet"]

        _LOGGER.debug(f"Player '{player_name}' {'placing' if bet else 'removing'} bet")

        # Verify round is active
        current_round = get_current_round(hass)
        if not current_round or current_round.get("status") != "active":
            connection.send_error(
                msg["id"], "no_active_round", "No active round to place bet"
            )
            return

        # Update bet status
        update_bet(hass, player_name, bet)

        # Send success response
        connection.send_result(
            msg["id"],
            {
                "success": True,
                "bet": bet,
            },
        )

        # Broadcast bet update
        hass.async_create_task(
            broadcast_event(
                hass,
                "bet_updated",
                {
                    "player_name": player_name,
                    "bet": bet,
                },
            )
        )

    except ValueError as e:
        _LOGGER.warning(f"Validation error in place_bet: {e}")
        connection.send_error(msg["id"], "validation_error", str(e))
    except Exception as e:
        _LOGGER.error(f"Error in place_bet: {e}", exc_info=True)
        connection.send_error(msg["id"], "internal_error", "Failed to place bet")


@callback
@websocket_api.websocket_command(SCHEMA_START_GAME)
def handle_start_game(
    hass: HomeAssistant,
    connection: ActiveConnection,
    msg: dict,
) -> None:
    """Handle start_game command (admin only).

    Initializes game with provided configuration.
    Admin validation placeholder for Epic 3.

    Args:
        hass: Home Assistant instance
        connection: WebSocket connection
        msg: Command message with config
    """
    try:
        config = msg["config"]

        # TODO: Verify admin status (future enhancement - Epic 3)
        # For Epic 2, accept start_game from any connection

        _LOGGER.info(f"Starting game with config: {config}")

        # Validate at least 2 players
        players = get_players(hass)
        if len(players) < 2:
            connection.send_error(
                msg["id"],
                "insufficient_players",
                "At least 2 players required to start game",
            )
            return

        # Initialize game with config (placeholder for Epic 5)
        initialize_game(hass, config)

        # Send success response
        connection.send_result(
            msg["id"],
            {
                "success": True,
                "game_started": True,
                "players": len(players),
            },
        )

        # Broadcast game_started event
        hass.async_create_task(
            broadcast_event(
                hass,
                "game_started",
                {
                    "config": config,
                    "players": len(players),
                },
            )
        )

    except ValueError as e:
        _LOGGER.warning(f"Validation error in start_game: {e}")
        connection.send_error(msg["id"], "validation_error", str(e))
    except Exception as e:
        _LOGGER.error(f"Error in start_game: {e}", exc_info=True)
        connection.send_error(msg["id"], "internal_error", "Failed to start game")


@websocket_api.websocket_command(SCHEMA_NEXT_SONG)
@websocket_api.async_response
async def handle_next_song(
    hass: HomeAssistant,
    connection: ActiveConnection,
    msg: dict,
) -> None:
    """Handle next_song command (admin only).

    Story 5.1: Selects random song from available_songs without repeating.
    Moves selected song to played_songs. Returns round information to admin.

    Note: This handler selects the song. Story 5.2 will add round initialization
    and broadcast round_started event to all clients.

    Args:
        hass: Home Assistant instance
        connection: WebSocket connection
        msg: Command message with type "beatsy/next_song"

    Response:
        Success: {"success": true, "result": {"round_number": int, "song_selected": true}}
        Error: {"success": false, "error": {"code": "playlist_exhausted", "message": "..."}}

    AC-1: Admin triggers command, song selected from available_songs
    AC-4: Returns error if playlist exhausted
    AC-5: Selected song won't repeat (moved to played_songs)
    """
    try:
        # TODO: Verify admin status (future enhancement - Epic 3)

        _LOGGER.info("Admin requested next song")

        # Story 5.1, AC-1: Select random song from available playlist
        # This function handles AC-1 through AC-7 (selection, validation, logging, etc.)
        selected_song = await select_random_song(hass)

        # Calculate round number (number of played songs = current round)
        # Story 5.2 will create full RoundState, but we need round number for response
        current_round_number = len(selected_song) if isinstance(selected_song, list) else 1

        # Get actual round number from played_songs count
        from .game_state import get_game_state
        state = get_game_state(hass)
        round_number = len(state.played_songs)

        _LOGGER.debug(
            "Song selected for round %d: %s by %s",
            round_number,
            selected_song.get("title", "Unknown"),
            selected_song.get("artist", "Unknown"),
        )

        # Story 5.1: Return success to admin with round number
        # Story 5.2 will handle round initialization and broadcasting round_started
        connection.send_result(
            msg["id"],
            {
                "success": True,
                "result": {
                    "round_number": round_number,
                    "song_selected": True,
                    "title": selected_song.get("title"),
                    "artist": selected_song.get("artist"),
                },
            },
        )

        # Story 5.2 TODO: After implementing initialize_round():
        # 1. Call initialize_round(hass, selected_song) to create RoundState
        # 2. Broadcast round_started event with song metadata (WITHOUT year)
        # For now, just log that song selection is complete
        _LOGGER.info("Song selection complete. Story 5.2 will add round initialization.")

    except PlaylistExhaustedError as e:
        # AC-4: Handle empty playlist gracefully
        _LOGGER.warning("Playlist exhausted when admin requested next song")
        connection.send_error(
            msg["id"],
            e.code,  # "playlist_exhausted"
            e.message,  # "All songs have been played..."
        )

    except ValueError as e:
        # Song validation error (missing required fields)
        _LOGGER.error(f"Song validation error in next_song: {e}", exc_info=True)
        connection.send_error(
            msg["id"],
            "invalid_song_data",
            f"Selected song has invalid structure: {str(e)}",
        )

    except Exception as e:
        # Unexpected error
        _LOGGER.error(f"Unexpected error in next_song: {e}", exc_info=True)
        connection.send_error(
            msg["id"], "internal_error", "Failed to select next song"
        )


async def broadcast_event(
    hass: HomeAssistant,
    event_type: str,
    data: dict,
    exclude_connection_id: str | None = None,
) -> None:
    """Broadcast event to all connected WebSocket clients.

    Args:
        hass: Home Assistant instance
        event_type: Event identifier (e.g., "player_joined", "round_started")
        data: Event payload
        exclude_connection_id: Optional connection ID to exclude from broadcast
    """
    try:
        message = {
            "type": "beatsy/event",
            "event_type": event_type,
            "data": data,
        }

        # Get connections from first entry's state
        entries = list(hass.data[DOMAIN].values())
        if not entries:
            _LOGGER.debug(f"No entries found to broadcast {event_type}")
            return

        state = entries[0]
        connections = state.get("websocket_connections", {})

        if not connections:
            _LOGGER.debug(f"No connections to broadcast {event_type}")
            return

        _LOGGER.debug(f"Broadcasting {event_type} to {len(connections)} clients")

        # Send to all connected clients (excluding specified connection if provided)
        failed_connections = []
        for connection_id, conn_info in connections.items():
            # Skip excluded connection (Story 4.3: joining player already has full list)
            if exclude_connection_id and connection_id == exclude_connection_id:
                continue

            try:
                connection = conn_info["connection"]
                # Send message using connection's send_message method
                connection.send_message(
                    websocket_api.event_message(connection_id, message)
                )
            except Exception as e:
                _LOGGER.warning(f"Failed to broadcast to {connection_id}: {e}")
                failed_connections.append(connection_id)

        # Clean up failed connections
        for connection_id in failed_connections:
            connections.pop(connection_id, None)

    except Exception as e:
        _LOGGER.error(f"Error in broadcast_event: {e}", exc_info=True)
