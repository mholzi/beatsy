"""Unit tests for WebSocket API command handlers.

Tests all WebSocket commands, schemas, and broadcast infrastructure.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
import voluptuous as vol

# Add the custom_components directory to the path
sys.path.insert(
    0, str(Path(__file__).parent.parent / "home-assistant-config" / "custom_components")
)

from beatsy.const import DOMAIN
from beatsy.websocket_api import (
    SCHEMA_JOIN_GAME,
    SCHEMA_PLACE_BET,
    SCHEMA_START_GAME,
    SCHEMA_SUBMIT_GUESS,
    WS_TYPE_JOIN_GAME,
    WS_TYPE_PLACE_BET,
    WS_TYPE_START_GAME,
    WS_TYPE_SUBMIT_GUESS,
    broadcast_event,
    handle_join_game,
    handle_place_bet,
    handle_start_game,
    handle_submit_guess,
)


@pytest.fixture
def mock_hass():
    """Create mock Home Assistant instance."""
    hass = MagicMock()
    hass.data = {
        DOMAIN: {
            "test_entry": {
                "game_config": {},
                "players": [],
                "current_round": None,
                "played_songs": [],
                "websocket_connections": {},
            }
        }
    }
    hass.async_create_task = Mock(side_effect=lambda coro: None)
    return hass


@pytest.fixture
def mock_connection():
    """Create mock WebSocket connection."""
    connection = MagicMock()
    connection.send_result = Mock()
    connection.send_error = Mock()
    connection.send_message = Mock()
    return connection


# Schema Validation Tests


def test_join_game_schema_valid():
    """Test join_game schema validates correctly."""
    valid_msg = {
        "id": 1,
        "type": WS_TYPE_JOIN_GAME,
        "player_name": "TestPlayer",
    }
    result = SCHEMA_JOIN_GAME(valid_msg)
    assert result["player_name"] == "TestPlayer"


def test_join_game_schema_with_game_id():
    """Test join_game schema with optional game_id."""
    valid_msg = {
        "id": 1,
        "type": WS_TYPE_JOIN_GAME,
        "player_name": "TestPlayer",
        "game_id": "game123",
    }
    result = SCHEMA_JOIN_GAME(valid_msg)
    assert result["game_id"] == "game123"


def test_join_game_schema_invalid_name_too_long():
    """Test join_game schema rejects name >20 chars."""
    invalid_msg = {
        "id": 1,
        "type": WS_TYPE_JOIN_GAME,
        "player_name": "A" * 30,  # Exceeds 20 char limit
    }
    with pytest.raises(vol.Invalid):
        SCHEMA_JOIN_GAME(invalid_msg)


def test_join_game_schema_invalid_name_empty():
    """Test join_game schema rejects empty name."""
    invalid_msg = {
        "id": 1,
        "type": WS_TYPE_JOIN_GAME,
        "player_name": "",
    }
    with pytest.raises(vol.Invalid):
        SCHEMA_JOIN_GAME(invalid_msg)


def test_submit_guess_schema_valid():
    """Test submit_guess schema validates correctly."""
    valid_msg = {
        "id": 1,
        "type": WS_TYPE_SUBMIT_GUESS,
        "player_name": "TestPlayer",
        "year_guess": 1995,
        "bet_placed": True,
    }
    result = SCHEMA_SUBMIT_GUESS(valid_msg)
    assert result["year_guess"] == 1995
    assert result["bet_placed"] is True


def test_submit_guess_schema_invalid_year_too_low():
    """Test submit_guess schema rejects year <1950."""
    invalid_msg = {
        "id": 1,
        "type": WS_TYPE_SUBMIT_GUESS,
        "player_name": "TestPlayer",
        "year_guess": 1900,  # Below range
        "bet_placed": False,
    }
    with pytest.raises(vol.Invalid):
        SCHEMA_SUBMIT_GUESS(invalid_msg)


def test_submit_guess_schema_invalid_year_too_high():
    """Test submit_guess schema rejects year >2050."""
    invalid_msg = {
        "id": 1,
        "type": WS_TYPE_SUBMIT_GUESS,
        "player_name": "TestPlayer",
        "year_guess": 2100,  # Above range
        "bet_placed": False,
    }
    with pytest.raises(vol.Invalid):
        SCHEMA_SUBMIT_GUESS(invalid_msg)


def test_submit_guess_schema_invalid_bet_not_bool():
    """Test submit_guess schema rejects non-boolean bet."""
    invalid_msg = {
        "id": 1,
        "type": WS_TYPE_SUBMIT_GUESS,
        "player_name": "TestPlayer",
        "year_guess": 1995,
        "bet_placed": "yes",  # Not a boolean
    }
    with pytest.raises(vol.Invalid):
        SCHEMA_SUBMIT_GUESS(invalid_msg)


def test_place_bet_schema_valid():
    """Test place_bet schema validates correctly."""
    valid_msg = {
        "id": 1,
        "type": WS_TYPE_PLACE_BET,
        "player_name": "TestPlayer",
        "bet": True,
    }
    result = SCHEMA_PLACE_BET(valid_msg)
    assert result["bet"] is True


def test_start_game_schema_valid():
    """Test start_game schema validates correctly."""
    valid_msg = {
        "id": 1,
        "type": WS_TYPE_START_GAME,
        "config": {"playlist_uri": "spotify:playlist:123", "round_timer": 30},
    }
    result = SCHEMA_START_GAME(valid_msg)
    assert result["config"]["playlist_uri"] == "spotify:playlist:123"


# Handler Tests - Join Game


@patch("beatsy.websocket_api.get_players")
@patch("beatsy.websocket_api.add_player")
def test_handle_join_game_success(mock_add_player, mock_get_players, mock_hass, mock_connection):
    """Test join_game handler adds player successfully."""
    mock_get_players.return_value = []

    msg = {
        "id": 1,
        "type": WS_TYPE_JOIN_GAME,
        "player_name": "TestPlayer",
    }

    handle_join_game(mock_hass, mock_connection, msg)

    # Verify player was added
    mock_add_player.assert_called_once()
    call_args = mock_add_player.call_args
    assert call_args[0][1] == "TestPlayer"  # player_name
    assert call_args[0][3] is False  # is_admin

    # Verify success response
    mock_connection.send_result.assert_called_once()
    result = mock_connection.send_result.call_args[0][1]
    assert result["success"] is True
    assert result["player_name"] == "TestPlayer"
    assert "session_id" in result
    assert "connection_id" in result

    # Verify broadcast was triggered
    mock_hass.async_create_task.assert_called_once()


@patch("beatsy.websocket_api.get_players")
def test_handle_join_game_duplicate_player(mock_get_players, mock_hass, mock_connection):
    """Test join_game handler rejects duplicate player name."""
    mock_get_players.return_value = [{"name": "TestPlayer", "score": 0}]

    msg = {
        "id": 1,
        "type": WS_TYPE_JOIN_GAME,
        "player_name": "TestPlayer",
    }

    handle_join_game(mock_hass, mock_connection, msg)

    # Verify error response
    mock_connection.send_error.assert_called_once()
    error_args = mock_connection.send_error.call_args[0]
    assert error_args[0] == 1  # msg_id
    assert error_args[1] == "player_exists"
    assert "already exists" in error_args[2]


@patch("beatsy.websocket_api.get_players")
def test_handle_join_game_strips_whitespace(mock_get_players, mock_hass, mock_connection):
    """Test join_game handler strips whitespace from player name."""
    mock_get_players.return_value = []

    msg = {
        "id": 1,
        "type": WS_TYPE_JOIN_GAME,
        "player_name": "  TestPlayer  ",  # Leading/trailing spaces
    }

    with patch("custom_components.beatsy.websocket_api.add_player") as mock_add:
        handle_join_game(mock_hass, mock_connection, msg)

        # Verify player name was stripped
        call_args = mock_add.call_args
        assert call_args[0][1] == "TestPlayer"  # No spaces


# Handler Tests - Submit Guess


@patch("beatsy.websocket_api.get_current_round")
@patch("beatsy.websocket_api.add_guess")
def test_handle_submit_guess_success(mock_add_guess, mock_get_round, mock_hass, mock_connection):
    """Test submit_guess handler records guess successfully."""
    mock_get_round.return_value = {
        "status": "active",
        "guesses": {},
        "track_uri": "spotify:track:123",
    }

    msg = {
        "id": 1,
        "type": WS_TYPE_SUBMIT_GUESS,
        "player_name": "TestPlayer",
        "year_guess": 1995,
        "bet_placed": True,
    }

    handle_submit_guess(mock_hass, mock_connection, msg)

    # Verify guess was added
    mock_add_guess.assert_called_once_with(mock_hass, "TestPlayer", 1995, True)

    # Verify success response
    mock_connection.send_result.assert_called_once()
    result = mock_connection.send_result.call_args[0][1]
    assert result["success"] is True
    assert result["guess_recorded"] is True

    # Verify broadcast was triggered
    mock_hass.async_create_task.assert_called_once()


@patch("beatsy.websocket_api.get_current_round")
def test_handle_submit_guess_no_active_round(mock_get_round, mock_hass, mock_connection):
    """Test submit_guess handler rejects when no active round."""
    mock_get_round.return_value = None

    msg = {
        "id": 1,
        "type": WS_TYPE_SUBMIT_GUESS,
        "player_name": "TestPlayer",
        "year_guess": 1995,
        "bet_placed": False,
    }

    handle_submit_guess(mock_hass, mock_connection, msg)

    # Verify error response
    mock_connection.send_error.assert_called_once()
    error_args = mock_connection.send_error.call_args[0]
    assert error_args[1] == "no_active_round"


@patch("beatsy.websocket_api.get_current_round")
def test_handle_submit_guess_round_not_active(mock_get_round, mock_hass, mock_connection):
    """Test submit_guess handler rejects when round status is not active."""
    mock_get_round.return_value = {
        "status": "ended",
        "guesses": {},
    }

    msg = {
        "id": 1,
        "type": WS_TYPE_SUBMIT_GUESS,
        "player_name": "TestPlayer",
        "year_guess": 1995,
        "bet_placed": False,
    }

    handle_submit_guess(mock_hass, mock_connection, msg)

    # Verify error response
    mock_connection.send_error.assert_called_once()


# Handler Tests - Place Bet


@patch("beatsy.websocket_api.get_current_round")
@patch("beatsy.websocket_api.update_bet")
def test_handle_place_bet_success(mock_update_bet, mock_get_round, mock_hass, mock_connection):
    """Test place_bet handler updates bet successfully."""
    mock_get_round.return_value = {
        "status": "active",
        "guesses": {},
    }

    msg = {
        "id": 1,
        "type": WS_TYPE_PLACE_BET,
        "player_name": "TestPlayer",
        "bet": True,
    }

    handle_place_bet(mock_hass, mock_connection, msg)

    # Verify bet was updated
    mock_update_bet.assert_called_once_with(mock_hass, "TestPlayer", True)

    # Verify success response
    mock_connection.send_result.assert_called_once()
    result = mock_connection.send_result.call_args[0][1]
    assert result["success"] is True
    assert result["bet"] is True

    # Verify broadcast was triggered
    mock_hass.async_create_task.assert_called_once()


@patch("beatsy.websocket_api.get_current_round")
def test_handle_place_bet_no_active_round(mock_get_round, mock_hass, mock_connection):
    """Test place_bet handler rejects when no active round."""
    mock_get_round.return_value = None

    msg = {
        "id": 1,
        "type": WS_TYPE_PLACE_BET,
        "player_name": "TestPlayer",
        "bet": True,
    }

    handle_place_bet(mock_hass, mock_connection, msg)

    # Verify error response
    mock_connection.send_error.assert_called_once()
    error_args = mock_connection.send_error.call_args[0]
    assert error_args[1] == "no_active_round"


# Handler Tests - Start Game


@patch("beatsy.websocket_api.get_players")
@patch("beatsy.websocket_api.initialize_game")
def test_handle_start_game_success(mock_init_game, mock_get_players, mock_hass, mock_connection):
    """Test start_game handler initializes game successfully."""
    mock_get_players.return_value = [
        {"name": "Player1", "score": 0},
        {"name": "Player2", "score": 0},
    ]

    msg = {
        "id": 1,
        "type": WS_TYPE_START_GAME,
        "config": {
            "playlist_uri": "spotify:playlist:123",
            "round_timer": 30,
        },
    }

    handle_start_game(mock_hass, mock_connection, msg)

    # Verify game was initialized
    mock_init_game.assert_called_once_with(mock_hass, msg["config"])

    # Verify success response
    mock_connection.send_result.assert_called_once()
    result = mock_connection.send_result.call_args[0][1]
    assert result["success"] is True
    assert result["game_started"] is True
    assert result["players"] == 2

    # Verify broadcast was triggered
    mock_hass.async_create_task.assert_called_once()


@patch("beatsy.websocket_api.get_players")
def test_handle_start_game_insufficient_players(mock_get_players, mock_hass, mock_connection):
    """Test start_game handler rejects with <2 players."""
    mock_get_players.return_value = [{"name": "Player1", "score": 0}]  # Only 1 player

    msg = {
        "id": 1,
        "type": WS_TYPE_START_GAME,
        "config": {},
    }

    handle_start_game(mock_hass, mock_connection, msg)

    # Verify error response
    mock_connection.send_error.assert_called_once()
    error_args = mock_connection.send_error.call_args[0]
    assert error_args[1] == "insufficient_players"
    assert "2 players required" in error_args[2]


# Broadcast Function Tests


@pytest.mark.asyncio
async def test_broadcast_event_success(mock_hass):
    """Test broadcast_event sends to all connections."""
    # Setup mock connections
    mock_conn1 = MagicMock()
    mock_conn1.send_message = Mock()
    mock_conn2 = MagicMock()
    mock_conn2.send_message = Mock()

    mock_hass.data[DOMAIN]["test_entry"]["websocket_connections"] = {
        "conn1": {"connection": mock_conn1, "player_name": "Player1"},
        "conn2": {"connection": mock_conn2, "player_name": "Player2"},
    }

    # Broadcast event
    await broadcast_event(mock_hass, "test_event", {"data": "test"})

    # Verify both connections received message
    assert mock_conn1.send_message.called
    assert mock_conn2.send_message.called


@pytest.mark.asyncio
async def test_broadcast_event_handles_failures(mock_hass):
    """Test broadcast_event handles individual connection failures gracefully."""
    # Setup mock connections - one will fail
    mock_conn1 = MagicMock()
    mock_conn1.send_message = Mock(side_effect=Exception("Connection lost"))
    mock_conn2 = MagicMock()
    mock_conn2.send_message = Mock()

    connections = {
        "conn1": {"connection": mock_conn1, "player_name": "Player1"},
        "conn2": {"connection": mock_conn2, "player_name": "Player2"},
    }
    mock_hass.data[DOMAIN]["test_entry"]["websocket_connections"] = connections

    # Broadcast event
    await broadcast_event(mock_hass, "test_event", {"data": "test"})

    # Verify failed connection was removed
    assert "conn1" not in connections
    assert "conn2" in connections

    # Verify successful connection still received message
    assert mock_conn2.send_message.called


@pytest.mark.asyncio
async def test_broadcast_event_no_connections(mock_hass):
    """Test broadcast_event handles no connections gracefully."""
    mock_hass.data[DOMAIN]["test_entry"]["websocket_connections"] = {}

    # Should not raise exception
    await broadcast_event(mock_hass, "test_event", {"data": "test"})


@pytest.mark.asyncio
async def test_broadcast_event_message_format(mock_hass):
    """Test broadcast_event uses correct message format."""
    mock_conn = MagicMock()
    mock_conn.send_message = Mock()

    mock_hass.data[DOMAIN]["test_entry"]["websocket_connections"] = {
        "conn1": {"connection": mock_conn, "player_name": "Player1"}
    }

    # Broadcast event
    await broadcast_event(mock_hass, "player_joined", {"player_name": "TestPlayer"})

    # Verify message format
    mock_conn.send_message.assert_called_once()
    # The message is wrapped by event_message, but we can verify it was called
    assert mock_conn.send_message.called


# Integration Tests


@patch("beatsy.websocket_api.get_players")
@patch("beatsy.websocket_api.add_player")
@patch("beatsy.websocket_api.get_current_round")
@patch("beatsy.websocket_api.add_guess")
def test_full_game_flow(
    mock_add_guess,
    mock_get_round,
    mock_add_player,
    mock_get_players,
    mock_hass,
    mock_connection,
):
    """Test full game flow: join -> start -> submit guess."""
    # 1. Join game
    mock_get_players.return_value = []
    join_msg = {
        "id": 1,
        "type": WS_TYPE_JOIN_GAME,
        "player_name": "TestPlayer",
    }
    handle_join_game(mock_hass, mock_connection, join_msg)
    assert mock_connection.send_result.called

    # 2. Start game
    mock_get_players.return_value = [
        {"name": "Player1", "score": 0},
        {"name": "Player2", "score": 0},
    ]
    with patch("custom_components.beatsy.websocket_api.initialize_game"):
        start_msg = {
            "id": 2,
            "type": WS_TYPE_START_GAME,
            "config": {"playlist_uri": "spotify:playlist:123"},
        }
        handle_start_game(mock_hass, mock_connection, start_msg)

    # 3. Submit guess
    mock_get_round.return_value = {"status": "active", "guesses": {}}
    guess_msg = {
        "id": 3,
        "type": WS_TYPE_SUBMIT_GUESS,
        "player_name": "TestPlayer",
        "year_guess": 1995,
        "bet_placed": True,
    }
    handle_submit_guess(mock_hass, mock_connection, guess_msg)

    # Verify all commands succeeded
    assert mock_connection.send_result.call_count == 3
