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
    add_guess,
    add_player,
    get_current_round,
    get_players,
    initialize_game,
    update_bet,
)

if TYPE_CHECKING:
    from homeassistant.components.websocket_api import ActiveConnection

_LOGGER = logging.getLogger(__name__)

# Command type constants
WS_TYPE_JOIN_GAME = "beatsy/join_game"
WS_TYPE_SUBMIT_GUESS = "beatsy/submit_guess"
WS_TYPE_PLACE_BET = "beatsy/place_bet"
WS_TYPE_START_GAME = "beatsy/start_game"
WS_TYPE_NEXT_SONG = "beatsy/next_song"

# Command schemas with voluptuous validation
SCHEMA_JOIN_GAME = websocket_api.BASE_COMMAND_MESSAGE_SCHEMA.extend(
    {
        vol.Required("type"): WS_TYPE_JOIN_GAME,
        vol.Required("player_name"): vol.All(str, vol.Length(min=1, max=20)),
        vol.Optional("game_id"): str,  # Future multi-game support
    }
)

SCHEMA_SUBMIT_GUESS = websocket_api.BASE_COMMAND_MESSAGE_SCHEMA.extend(
    {
        vol.Required("type"): WS_TYPE_SUBMIT_GUESS,
        vol.Required("player_name"): vol.All(str, vol.Length(min=1, max=20)),
        vol.Required("year_guess"): vol.All(int, vol.Range(min=1950, max=2050)),
        vol.Required("bet_placed"): bool,
    }
)

SCHEMA_PLACE_BET = websocket_api.BASE_COMMAND_MESSAGE_SCHEMA.extend(
    {
        vol.Required("type"): WS_TYPE_PLACE_BET,
        vol.Required("player_name"): vol.All(str, vol.Length(min=1, max=20)),
        vol.Required("bet"): bool,
    }
)

SCHEMA_START_GAME = websocket_api.BASE_COMMAND_MESSAGE_SCHEMA.extend(
    {
        vol.Required("type"): WS_TYPE_START_GAME,
        vol.Required("config"): dict,  # Game configuration
    }
)

SCHEMA_NEXT_SONG = websocket_api.BASE_COMMAND_MESSAGE_SCHEMA.extend(
    {
        vol.Required("type"): WS_TYPE_NEXT_SONG,
    }
)


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
        player_name = msg["player_name"].strip()
        game_id = msg.get("game_id")  # Optional, future use

        _LOGGER.info(f"Player '{player_name}' joining game")

        # Check if player already exists
        players = get_players(hass)
        if any(p["name"] == player_name for p in players):
            connection.send_error(
                msg["id"], "player_exists", f"Player '{player_name}' already exists"
            )
            return

        # Add player to game state
        session_id = str(uuid.uuid4())
        add_player(hass, player_name, session_id, is_admin=False)

        # Track WebSocket connection
        connection_id = str(uuid.uuid4())

        # Get the first entry's state for connection tracking
        entries = list(hass.data[DOMAIN].values())
        if entries:
            state = entries[0]
            if "websocket_connections" not in state:
                state["websocket_connections"] = {}

            state["websocket_connections"][connection_id] = {
                "player_name": player_name,
                "connected_at": time.time(),
                "last_ping": time.time(),
                "connection": connection,
            }

        # Send success response
        connection.send_result(
            msg["id"],
            {
                "success": True,
                "player_name": player_name,
                "session_id": session_id,
                "connection_id": connection_id,
            },
        )

        # Broadcast player_joined event to all clients
        hass.async_create_task(
            broadcast_event(
                hass,
                "player_joined",
                {
                    "player_name": player_name,
                    "total_players": len(get_players(hass)),
                },
            )
        )

    except ValueError as e:
        _LOGGER.warning(f"Validation error in join_game: {e}")
        connection.send_error(msg["id"], "validation_error", str(e))
    except Exception as e:
        _LOGGER.error(f"Error in join_game: {e}", exc_info=True)
        connection.send_error(msg["id"], "internal_error", "Failed to join game")


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


@callback
@websocket_api.websocket_command(SCHEMA_NEXT_SONG)
def handle_next_song(
    hass: HomeAssistant,
    connection: ActiveConnection,
    msg: dict,
) -> None:
    """Handle next_song command (admin only).

    Advances to next song/round.
    Placeholder for Epic 5 song selection logic.

    Args:
        hass: Home Assistant instance
        connection: WebSocket connection
        msg: Command message
    """
    try:
        # TODO: Verify admin status (future enhancement - Epic 3)

        _LOGGER.info("Advancing to next song")

        # Placeholder for Epic 5 (song selection and playback)
        # For Epic 2, just acknowledge command

        # Send success response
        connection.send_result(
            msg["id"],
            {
                "success": True,
                "message": "Next song logic not yet implemented (Epic 5)",
            },
        )

        # Broadcast next_song event (placeholder)
        hass.async_create_task(
            broadcast_event(
                hass,
                "next_song_requested",
                {
                    "message": "Next song functionality coming in Epic 5",
                },
            )
        )

    except Exception as e:
        _LOGGER.error(f"Error in next_song: {e}", exc_info=True)
        connection.send_error(
            msg["id"], "internal_error", "Failed to advance to next song"
        )


async def broadcast_event(
    hass: HomeAssistant,
    event_type: str,
    data: dict,
) -> None:
    """Broadcast event to all connected WebSocket clients.

    Args:
        hass: Home Assistant instance
        event_type: Event identifier (e.g., "player_joined", "round_started")
        data: Event payload
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

        # Send to all connected clients
        failed_connections = []
        for connection_id, conn_info in connections.items():
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
