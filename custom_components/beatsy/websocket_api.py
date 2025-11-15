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
    initialize_round,
    prepare_round_started_payload,
    reset_game,
    reset_game_async,
    select_random_song,
    update_bet,
)
from .validation import validate_player_name, validate_year_guess
from .rate_limiter import RATE_LIMITS

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
WS_TYPE_SKIP_SONG = "beatsy/skip_song"  # Story 7.5
WS_TYPE_RESET_GAME = "beatsy/reset_game"  # Story 5.7

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
    vol.Optional("force", default=False): bool,  # Story 7.3: Force start despite conflict warning
}

SCHEMA_NEXT_SONG = {
    vol.Required("type"): WS_TYPE_NEXT_SONG,
}

SCHEMA_SKIP_SONG = {
    vol.Required("type"): WS_TYPE_SKIP_SONG,
}

SCHEMA_RESET_GAME = {
    vol.Required("type"): WS_TYPE_RESET_GAME,
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

    Story 10.6: Rate limiting applied - 1 join per 5 seconds per connection.

    Args:
        hass: Home Assistant instance
        connection: WebSocket connection
        msg: Command message with player_name
    """
    try:
        # Story 10.6: Rate limiting check (1 join per 5 seconds per connection)
        rate_limiter = hass.data[DOMAIN].get("rate_limiter")
        if rate_limiter:
            # Use connection ID as rate limit key
            rate_key = f"join_game:{id(connection)}"
            limit = RATE_LIMITS["join_game"]
            is_allowed, retry_after = rate_limiter.check_limit(rate_key, limit)

            if not is_allowed:
                _LOGGER.warning(
                    "Rate limit exceeded for join_game: retry_after=%.1fs",
                    retry_after or 0,
                )
                connection.send_error(
                    msg["id"],
                    "rate_limit_exceeded",
                    f"Too many join attempts. Please wait {int(retry_after or 5)} seconds.",
                )
                return

        requested_name = msg["player_name"].strip()
        game_id = msg.get("game_id")  # Optional, future use

        # Story 10.5: Validate and sanitize player name
        validation_result = validate_player_name(requested_name)
        if not validation_result.valid:
            _LOGGER.warning(
                f"Player name validation failed: {requested_name} - {validation_result.error_message}"
            )
            connection.send_error(
                msg["id"], "invalid_player_name", validation_result.error_message
            )
            return

        # Use sanitized name for safety
        sanitized_name = validation_result.sanitized_value

        # Find unique name (handles duplicates automatically)
        unique_name = find_unique_name(hass, sanitized_name)
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
                "name_adjusted": name_adjusted or (unique_name != sanitized_name),
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

        # Story 10.5: Validate player name
        name_validation = validate_player_name(player_name)
        if not name_validation.valid:
            _LOGGER.warning(
                f"Invalid player name in reconnect: {player_name} - {name_validation.error_message}"
            )
            connection.send_result(
                msg["id"],
                {
                    "success": False,
                    "reason": "invalid_player_name",
                },
            )
            return

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

    Story 10.6: Rate limiting applied - 5 toggles per second per player.

    Args:
        hass: Home Assistant instance
        connection: WebSocket connection
        msg: Command message with player_name, bet
    """
    try:
        player_name = msg["player_name"]
        bet = msg["bet"]

        # Story 10.6: Rate limiting check (5 toggles per second per player)
        rate_limiter = hass.data[DOMAIN].get("rate_limiter")
        if rate_limiter:
            rate_key = f"place_bet:{player_name}"
            limit = RATE_LIMITS["place_bet"]
            is_allowed, retry_after = rate_limiter.check_limit(rate_key, limit)

            if not is_allowed:
                _LOGGER.warning(
                    "Rate limit exceeded for place_bet (player=%s): retry_after=%.1fs",
                    player_name,
                    retry_after or 0,
                )
                connection.send_error(
                    msg["id"],
                    "rate_limit_exceeded",
                    "Bet toggle too fast. Please slow down.",
                )
                return

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

        # Broadcast bet placement
        hass.async_create_task(
            broadcast_event(
                hass,
                "bet_placed",
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


@websocket_api.websocket_command(SCHEMA_START_GAME)
@websocket_api.async_response
async def handle_start_game(
    hass: HomeAssistant,
    connection: ActiveConnection,
    msg: dict,
) -> None:
    """Handle start_game command (admin only).

    Story 7.3: Checks media player state before starting game. If player is
    currently playing or paused, returns conflict_warning to admin. Admin can
    then retry with force=true to proceed and save current state.

    Args:
        hass: Home Assistant instance
        connection: WebSocket connection
        msg: Command message with config and optional force flag

    Response:
        Success (no conflict): {success: true, game_started: true, players: int}
        Conflict warning: {conflict_warning: true, current_media: {title, artist, state}}
        Force success: {success: true, game_started: true, state_saved: true}
    """
    try:
        from .spotify_service import (
            get_media_player_state,
            save_player_state,
            should_warn_conflict,
        )

        config = msg["config"]
        force = msg.get("force", False)

        # TODO: Verify admin status (future enhancement - Epic 3)
        # For Epic 2, accept start_game from any connection

        _LOGGER.info("Starting game with config: %s (force=%s)", config, force)

        # Validate at least 2 players
        players = get_players(hass)
        if len(players) < 2:
            connection.send_error(
                msg["id"],
                "insufficient_players",
                "At least 2 players required to start game",
            )
            return

        # Story 7.3: Check media player state before starting
        media_player_entity_id = config.get("media_player_entity_id")

        if media_player_entity_id and not force:
            # Query current media player state
            player_state = await get_media_player_state(hass, media_player_entity_id)

            # Check if conflict warning should be shown
            if should_warn_conflict(player_state):
                # AC-1: Show conflict warning to admin
                _LOGGER.info(
                    "Media player %s is %s, returning conflict warning to admin",
                    media_player_entity_id,
                    player_state.state,
                )

                # AC-2: Return conflict_warning response with current media info
                connection.send_result(
                    msg["id"],
                    {
                        "conflict_warning": True,
                        "current_media": {
                            "entity_id": player_state.entity_id,
                            "title": player_state.media_title or "Unknown",
                            "artist": player_state.media_artist or "Unknown",
                            "state": player_state.state,
                        },
                    },
                )
                return

        # AC-3: If force=true or no conflict, save state and proceed
        if media_player_entity_id and force:
            # Get fresh state for saving
            player_state = await get_media_player_state(hass, media_player_entity_id)
            if player_state is not None:
                # Save state for restoration (Story 7.6)
                save_player_state(hass, player_state)

        # Initialize game with config (placeholder for Epic 5)
        initialize_game(hass, config)

        # Send success response
        connection.send_result(
            msg["id"],
            {
                "success": True,
                "game_started": True,
                "players": len(players),
                "state_saved": force and media_player_entity_id is not None,
            },
        )

        # Broadcast game_started event
        await broadcast_event(
            hass,
            "game_started",
            {
                "config": config,
                "players": len(players),
            },
        )

    except ValueError as e:
        _LOGGER.warning("Validation error in start_game: %s", e)
        connection.send_error(msg["id"], "validation_error", str(e))
    except Exception as e:
        _LOGGER.error("Error in start_game: %s", e, exc_info=True)
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

        # Story 5.4, AC-9: Manual round end support
        # If there's a current round, end it before starting new round
        from .game_state import get_game_state, end_round
        state = get_game_state(hass)

        if state.current_round is not None:
            # Cancel timer task if it exists and is still running
            if state.round_timer_task is not None and not state.round_timer_task.done():
                state.round_timer_task.cancel()
                _LOGGER.info(
                    "Cancelled timer task for round %d (manual round end by admin)",
                    state.current_round.round_number,
                )

            # End current round (calculates scores, broadcasts round_ended event)
            # This ensures proper round lifecycle: active -> ended -> new round
            await end_round(hass)
            _LOGGER.info("Round ended manually by admin before starting new round")

        # Story 5.1, AC-1: Select random song from available playlist
        # This function handles AC-1 through AC-7 (selection, validation, logging, etc.)
        selected_song = await select_random_song(hass)

        # Story 5.2, AC-4: Initialize round with selected song
        # Creates RoundState with round_number, song, started_at, timer_duration, status, guesses
        round_state = await initialize_round(hass, selected_song)

        # Story 5.2, AC-3: Prepare round_started payload (excludes year field)
        payload = prepare_round_started_payload(round_state)

        # Story 5.2, AC-3: Broadcast round_started event to ALL connected clients
        # This includes admin AND all players - triggers Epic 8 active round UI
        await broadcast_event(hass, "round_started", payload)

        # Story 5.2, AC-6: Log round start with player count
        from .game_state import get_game_state
        state = get_game_state(hass)
        players_count = len(state.players)

        _LOGGER.info(
            "Round %d started: '%s' by %s (%d players connected)",
            round_state.round_number,
            selected_song.get("title"),
            selected_song.get("artist"),
            players_count,
        )
        _LOGGER.debug(
            "Round state: started_at=%f, timer_duration=%ds",
            round_state.started_at,
            round_state.timer_duration,
        )

        # Story 5.2, AC-4: Return success to admin with round_number
        connection.send_result(
            msg["id"],
            {
                "success": True,
                "result": {
                    "round_number": round_state.round_number,
                },
            },
        )

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


@websocket_api.websocket_command(SCHEMA_SKIP_SONG)
@websocket_api.async_response
async def handle_skip_song(
    hass: HomeAssistant,
    connection: ActiveConnection,
    msg: dict,
) -> None:
    """Handle skip_song command (admin only) - replaces failed song with new one.

    Story 7.5, Task 4: Allows admin to manually skip a song that failed to play.
    Similar to next_song but triggered during playback errors. Selects a new random
    song and starts a new round immediately.

    Args:
        hass: Home Assistant instance
        connection: WebSocket connection (admin)
        msg: Command message with type "beatsy/skip_song"

    Response:
        Success: {"success": true, "result": {"round_number": int}}
        Error: {"success": false, "error": {"code": "...", "message": "..."}}

    Error Codes:
        - playlist_exhausted: No more songs available to play
        - invalid_song_data: Selected song has invalid structure
        - internal_error: Unexpected failure during song selection

    Flow:
        1. Select new random song (select_random_song)
        2. Initialize new round with selected song (initialize_round)
        3. Broadcast round_started event to all clients
        4. Return success with round_number to admin
    """
    try:
        # TODO: Verify admin status (future enhancement - Epic 3)

        _LOGGER.info("Admin requested skip to next song (playback error recovery)")

        # Story 7.5: Select new random song to replace failed one
        selected_song = await select_random_song(hass)

        # Initialize new round with selected song
        round_state = await initialize_round(hass, selected_song)

        # Prepare round_started payload (excludes year field for security)
        payload = prepare_round_started_payload(round_state)

        # Broadcast round_started event to all connected clients
        await broadcast_event(hass, "round_started", payload)

        # Log skip action
        from .game_state import get_game_state
        state = get_game_state(hass)
        players_count = len(state.players)

        _LOGGER.info(
            "Skipped to Round %d: '%s' by %s (%d players connected)",
            round_state.round_number,
            selected_song.get("title"),
            selected_song.get("artist"),
            players_count,
        )

        # Return success to admin with round_number
        connection.send_result(
            msg["id"],
            {
                "success": True,
                "result": {
                    "round_number": round_state.round_number,
                },
            },
        )

    except PlaylistExhaustedError as e:
        # Handle empty playlist gracefully
        _LOGGER.warning("Playlist exhausted when admin requested skip song")
        connection.send_error(
            msg["id"],
            e.code,  # "playlist_exhausted"
            e.message,
        )

    except ValueError as e:
        # Song validation error (missing required fields)
        _LOGGER.error(f"Song validation error in skip_song: {e}", exc_info=True)
        connection.send_error(
            msg["id"],
            "invalid_song_data",
            f"Selected song has invalid structure: {str(e)}",
        )

    except Exception as e:
        # Unexpected error
        _LOGGER.error(f"Unexpected error in skip_song: {e}", exc_info=True)
        connection.send_error(
            msg["id"], "internal_error", "Failed to skip to next song"
        )


@websocket_api.websocket_command(SCHEMA_SUBMIT_GUESS)
@websocket_api.async_response
async def handle_submit_guess(
    hass: HomeAssistant,
    connection: ActiveConnection,
    msg: dict,
) -> None:
    """Handle submit_guess command (player action).

    Story 5.3: Records player's year guess and bet choice during active round.
    Story 10.6: Rate limiting applied - 1 guess per 2 seconds per player.
    Validates timing (with 2s grace period), prevents duplicates, stores guess.

    Validation Chain (fail-fast):
    1. Rate limiting check (Story 10.6)
    2. Active round check → status == "active"
    3. Timer validation → elapsed <= (timer_duration + 2s grace)
    4. Duplicate check → player_name not in guesses
    5. Storage → add_guess() appends to current_round.guesses

    Args:
        hass: Home Assistant instance
        connection: WebSocket connection
        msg: Command message with:
            - player_name: str (1-20 chars, validated by schema)
            - year_guess: int (1950-2050, validated by schema)
            - bet_placed: bool

    Response:
        Success: {"success": true, "result": {"message": "Guess submitted"}}
        Error: {"success": false, "error": {"code": "...", "message": "..."}}

    Error Codes:
        - rate_limit_exceeded: Too many guesses in time window (Story 10.6)
        - no_active_round: No round in progress or round ended
        - timer_expired: Submission after timer + grace period
        - already_submitted: Player already submitted guess for this round
        - guess_storage_failed: Unexpected error storing guess

    AC-1: Schema validation (player_name, year_guess, bet_placed) ✓ (decorator)
    AC-2: Active round validation (current_round exists, status == "active")
    AC-3: Timer validation (elapsed <= timer_duration + 2s grace period)
    AC-4: Duplicate prevention (player_name not in guesses)
    AC-5: Guess storage (add_guess() with timestamp)
    AC-6: Response latency (<100ms target)
    AC-7: Comprehensive logging (INFO/WARNING with context)
    AC-8: Integration with Story 5.2 RoundState
    AC-9: Error handling (no crashes, consistent state)
    """
    try:
        player_name = msg["player_name"]
        year_guess = msg["year_guess"]
        bet_placed = msg["bet_placed"]

        # Story 10.6: Rate limiting check (1 guess per 2 seconds per player)
        rate_limiter = hass.data[DOMAIN].get("rate_limiter")
        if rate_limiter:
            rate_key = f"submit_guess:{player_name}"
            limit = RATE_LIMITS["submit_guess"]
            is_allowed, retry_after = rate_limiter.check_limit(rate_key, limit)

            if not is_allowed:
                _LOGGER.warning(
                    "Rate limit exceeded for submit_guess (player=%s): retry_after=%.1fs",
                    player_name,
                    retry_after or 0,
                )
                connection.send_error(
                    msg["id"],
                    "rate_limit_exceeded",
                    f"Guess submitted too quickly. Please wait {int(retry_after or 2)} seconds.",
                )
                return

        # Story 10.5: Validate player name
        name_validation = validate_player_name(player_name)
        if not name_validation.valid:
            _LOGGER.warning(
                f"Invalid player name in submit_guess: {player_name} - {name_validation.error_message}"
            )
            connection.send_error(
                msg["id"], "invalid_player_name", name_validation.error_message
            )
            return

        # AC-2: Validate active round exists
        current_round = get_current_round(hass)

        if current_round is None or current_round.status != "active":
            # AC-2, AC-7: Log WARNING for no active round
            _LOGGER.warning(
                "Player %s attempted guess with no active round (status: %s)",
                player_name,
                current_round.status if current_round else "None",
            )
            connection.send_error(
                msg["id"],
                "no_active_round",
                "No active round to submit guess to",
            )
            return

        # Story 10.5: Validate year guess against configured range
        # Get year range from game state
        from .game_state import get_game_state
        state = get_game_state(hass)
        min_year = getattr(state, 'year_range_min', 1950)
        max_year = getattr(state, 'year_range_max', 2050)

        year_validation = validate_year_guess(year_guess, min_year, max_year)
        if not year_validation.valid:
            _LOGGER.warning(
                f"Invalid year guess from {player_name}: {year_guess} - {year_validation.error_message}"
            )
            connection.send_error(
                msg["id"], "invalid_year_guess", year_validation.error_message
            )
            return

        # Use validated year value
        year_guess = year_validation.sanitized_value

        # AC-3: Validate timer hasn't expired (with 2s grace period)
        # Server timestamp authority - calculate elapsed time from server clock
        elapsed = time.time() - current_round.started_at
        deadline = current_round.timer_duration + 2.0  # 2-second grace period

        if elapsed > deadline:
            # AC-3, AC-7: Log WARNING for late submission with timing details
            _LOGGER.warning(
                "Late guess from %s: %.1fs > %.1fs deadline (round %d)",
                player_name,
                elapsed,
                deadline,
                current_round.round_number,
            )
            connection.send_error(
                msg["id"],
                "timer_expired",
                "Round has ended, submission too late",
            )
            return

        # AC-4: Check for duplicate submission (first submission wins)
        # Linear search O(n) acceptable for 20 players
        for existing_guess in current_round.guesses:
            if existing_guess["player_name"] == player_name:
                # AC-4, AC-7: Log WARNING for duplicate attempt
                _LOGGER.warning(
                    "Duplicate guess attempt from %s (round %d)",
                    player_name,
                    current_round.round_number,
                )
                connection.send_error(
                    msg["id"],
                    "already_submitted",
                    "You have already submitted a guess for this round",
                )
                return

        # AC-5: Store guess via add_guess() from Story 5.2
        # This function appends to current_round.guesses with structure:
        # {player_name, year_guess, bet_placed, submitted_at: time.time()}
        add_guess(hass, player_name, year_guess, bet_placed)

        # AC-6, AC-7: Log INFO for successful submission with context
        _LOGGER.info(
            "Guess submitted: player=%s, year=%d, bet=%s, round=%d",
            player_name,
            year_guess,
            bet_placed,
            current_round.round_number,
        )

        # AC-6: Return success response (target <100ms)
        connection.send_result(
            msg["id"],
            {
                "success": True,
                "result": {"message": "Guess submitted"},
            },
        )

    except Exception as e:
        # AC-9: Error handling for unexpected failures
        # Don't crash - log ERROR and return consistent error response
        _LOGGER.error(
            "Guess storage failed: player=%s, error=%s",
            msg.get("player_name", "unknown"),
            str(e),
            exc_info=True,
        )
        connection.send_error(
            msg["id"],
            "guess_storage_failed",
            "Failed to store guess",
        )


@websocket_api.async_response
@websocket_api.websocket_command(SCHEMA_RESET_GAME)
async def handle_reset_game(
    hass: HomeAssistant,
    connection: ActiveConnection,
    msg: dict,
) -> None:
    """Handle reset_game command (admin only).

    Story 5.7: Resets all ephemeral game state to prepare for new game session.
    Story 7.6: Restores media player state before clearing game state.
    Clears players, current_round, played_songs, and restores available_songs from original_playlist.
    Broadcasts game_reset event to all connected clients.

    Args:
        hass: Home Assistant instance
        connection: WebSocket connection (admin)
        msg: Command message with type "beatsy/reset_game"

    Response:
        Success: {"success": true}
        Error: {"success": false, "error": {"code": "...", "message": "..."}}

    AC-6: Admin sends beatsy/reset_game command, handler calls reset_game_async(hass)
    AC-3: Broadcast game_reset event to all clients with timestamp
    Story 7.6 AC-1: Restore media player state during reset
    """
    try:
        # TODO: Verify admin status (future enhancement - Epic 3)
        # For now, accept reset_game from any connection

        _LOGGER.info("Game reset requested by WebSocket connection %s", connection.id)

        # AC-1, AC-2, AC-5: Call reset_game_async() function (async with media player restoration)
        # Story 7.6: This will restore media player state before clearing game state
        await reset_game_async(hass)

        # AC-3: Broadcast game_reset event to ALL clients
        hass.async_create_task(
            broadcast_event(
                hass,
                "game_reset",
                {
                    "timestamp": time.time(),
                    "message": "Game has been reset. Please return to registration.",
                },
            )
        )

        # Send success response to admin
        connection.send_result(
            msg["id"],
            {
                "success": True,
            },
        )

        _LOGGER.info("Game reset completed successfully")

    except Exception as e:
        _LOGGER.error("Error in reset_game: %s", e, exc_info=True)
        connection.send_error(
            msg["id"],
            "reset_failed",
            f"Failed to reset game: {str(e)}",
        )


# Import broadcast_event from websocket_handler (Epic 6, Story 6.1)
# This replaces the old implementation with the new asyncio.gather() version
from .websocket_handler import broadcast_event  # noqa: F401
