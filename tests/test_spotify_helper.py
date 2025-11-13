"""Tests for Beatsy Spotify helper module.

Tests cover:
- Media player detection logic
- Cast device identification
- Empty list handling
- Error handling and edge cases
- MediaPlayerInfo dataclass structure
"""
import logging
import sys
from pathlib import Path
from typing import get_type_hints
from unittest.mock import Mock, patch

import pytest
from homeassistant.core import HomeAssistant, State

# Add the custom_components directory to the path
sys.path.insert(
    0, str(Path(__file__).parent.parent / "home-assistant-config" / "custom_components")
)

from beatsy.spotify_helper import (
    MediaPlayerInfo,
    get_spotify_media_players,
    _supports_spotify_playback,
    SUPPORT_PLAY_MEDIA,
)


@pytest.fixture
def mock_hass():
    """Create a mock Home Assistant instance."""
    hass = Mock(spec=HomeAssistant)
    hass.states = Mock()
    return hass


def create_mock_state(
    entity_id: str,
    state: str = "idle",
    friendly_name: str | None = None,
    supported_features: int = 0,
) -> State:
    """Create a mock State object for testing.

    Args:
        entity_id: Media player entity ID
        state: Player state (idle, playing, paused, off, unavailable, unknown)
        friendly_name: Human-readable name (None to omit)
        supported_features: Feature flags bitmask

    Returns:
        Mock State object
    """
    attributes = {"supported_features": supported_features}
    if friendly_name:
        attributes["friendly_name"] = friendly_name

    mock_state = Mock(spec=State)
    mock_state.entity_id = entity_id
    mock_state.state = state
    mock_state.attributes = attributes

    return mock_state


# Test MediaPlayerInfo dataclass structure (AC-4)


def test_media_player_info_dataclass_fields():
    """Test MediaPlayerInfo has correct fields with proper types."""
    # Create instance
    player = MediaPlayerInfo(
        entity_id="media_player.test",
        friendly_name="Test Player",
        state="idle",
        supports_play_media=True,
    )

    # Verify fields
    assert player.entity_id == "media_player.test"
    assert player.friendly_name == "Test Player"
    assert player.state == "idle"
    assert player.supports_play_media is True

    # Verify type hints
    hints = get_type_hints(MediaPlayerInfo)
    assert hints["entity_id"] == str
    assert hints["friendly_name"] == str
    assert hints["state"] == str
    assert hints["supports_play_media"] == bool


def test_media_player_info_default_supports_play_media():
    """Test supports_play_media defaults to True."""
    player = MediaPlayerInfo(
        entity_id="media_player.test",
        friendly_name="Test",
        state="idle",
    )
    assert player.supports_play_media is True


# Test _supports_spotify_playback helper (AC-2)


def test_supports_spotify_cast_device():
    """Test Cast device identified by entity_id containing 'cast'."""
    state = create_mock_state("media_player.living_room_cast", "idle")
    assert _supports_spotify_playback(state) is True


def test_supports_spotify_chromecast_device():
    """Test Chromecast device identified by entity_id containing 'chromecast'."""
    state = create_mock_state("media_player.chromecast_bedroom", "idle")
    assert _supports_spotify_playback(state) is True


def test_supports_spotify_play_media_feature():
    """Test device with SUPPORT_PLAY_MEDIA feature flag."""
    state = create_mock_state(
        "media_player.speaker", "idle", supported_features=SUPPORT_PLAY_MEDIA
    )
    assert _supports_spotify_playback(state) is True


def test_supports_spotify_no_support():
    """Test device without Cast or SUPPORT_PLAY_MEDIA returns False."""
    state = create_mock_state("media_player.basic_player", "idle", supported_features=0)
    assert _supports_spotify_playback(state) is False


def test_supports_spotify_case_insensitive():
    """Test Cast detection is case-insensitive."""
    state = create_mock_state("media_player.Living_Room_CAST", "idle")
    assert _supports_spotify_playback(state) is True


# Test get_spotify_media_players basic detection (AC-1)


@pytest.mark.asyncio
async def test_get_spotify_media_players_basic(mock_hass):
    """Test basic media player detection."""
    # Setup mock states
    mock_states = [
        create_mock_state(
            "media_player.living_room_speaker",
            "idle",
            "Living Room Speaker",
            SUPPORT_PLAY_MEDIA,
        ),
    ]
    mock_hass.states.async_all.return_value = mock_states

    # Call function
    players = await get_spotify_media_players(mock_hass)

    # Verify results
    assert len(players) == 1
    assert players[0].entity_id == "media_player.living_room_speaker"
    assert players[0].friendly_name == "Living Room Speaker"
    assert players[0].state == "idle"
    assert players[0].supports_play_media is True

    # Verify mock called correctly
    mock_hass.states.async_all.assert_called_once_with("media_player")


@pytest.mark.asyncio
async def test_get_spotify_media_players_multiple(mock_hass):
    """Test detection of multiple media players."""
    mock_states = [
        create_mock_state("media_player.cast_1", "idle", "Cast Device 1"),
        create_mock_state("media_player.cast_2", "playing", "Cast Device 2"),
        create_mock_state(
            "media_player.speaker", "paused", "Smart Speaker", SUPPORT_PLAY_MEDIA
        ),
    ]
    mock_hass.states.async_all.return_value = mock_states

    players = await get_spotify_media_players(mock_hass)

    assert len(players) == 3
    assert players[0].entity_id == "media_player.cast_1"
    assert players[1].entity_id == "media_player.cast_2"
    assert players[2].entity_id == "media_player.speaker"


# Test Cast device detection (AC-2)


@pytest.mark.asyncio
async def test_cast_device_detected_without_features(mock_hass):
    """Test Cast device detected even without SUPPORT_PLAY_MEDIA feature."""
    mock_states = [
        create_mock_state(
            "media_player.chromecast_living_room",
            "idle",
            "Living Room Chromecast",
            supported_features=0,  # No features set
        ),
    ]
    mock_hass.states.async_all.return_value = mock_states

    players = await get_spotify_media_players(mock_hass)

    assert len(players) == 1
    assert "cast" in players[0].entity_id


# Test unavailable player filtering (AC-3)


@pytest.mark.asyncio
async def test_unavailable_player_filtered(mock_hass):
    """Test unavailable players are excluded."""
    mock_states = [
        create_mock_state("media_player.offline_speaker", "unavailable", "Offline"),
        create_mock_state("media_player.online_cast", "idle", "Online Cast"),
    ]
    mock_hass.states.async_all.return_value = mock_states

    players = await get_spotify_media_players(mock_hass)

    assert len(players) == 1
    assert players[0].entity_id == "media_player.online_cast"


@pytest.mark.asyncio
async def test_unknown_player_filtered(mock_hass):
    """Test players with 'unknown' state are excluded."""
    mock_states = [
        create_mock_state("media_player.unknown_device", "unknown", "Unknown Device"),
        create_mock_state("media_player.known_cast", "off", "Known Cast"),
    ]
    mock_hass.states.async_all.return_value = mock_states

    players = await get_spotify_media_players(mock_hass)

    assert len(players) == 1
    assert players[0].entity_id == "media_player.known_cast"


# Test friendly_name fallback (AC-4)


@pytest.mark.asyncio
async def test_friendly_name_fallback_to_entity_id(mock_hass):
    """Test friendly_name falls back to entity_id when attribute missing."""
    mock_states = [
        create_mock_state(
            "media_player.test_speaker",
            "idle",
            friendly_name=None,  # No friendly_name
            supported_features=SUPPORT_PLAY_MEDIA,
        ),
    ]
    mock_hass.states.async_all.return_value = mock_states

    players = await get_spotify_media_players(mock_hass)

    assert len(players) == 1
    assert players[0].friendly_name == "media_player.test_speaker"


# Test empty list handling (AC-3)


@pytest.mark.asyncio
async def test_no_players_returns_empty_list(mock_hass, caplog):
    """Test empty list when no players exist."""
    mock_hass.states.async_all.return_value = []

    with caplog.at_level(logging.WARNING):
        players = await get_spotify_media_players(mock_hass)

    assert players == []
    assert "No Spotify-capable media players found" in caplog.text


@pytest.mark.asyncio
async def test_all_unavailable_returns_empty_list(mock_hass, caplog):
    """Test empty list when all players are unavailable."""
    mock_states = [
        create_mock_state("media_player.offline_1", "unavailable"),
        create_mock_state("media_player.offline_2", "unavailable"),
    ]
    mock_hass.states.async_all.return_value = mock_states

    with caplog.at_level(logging.WARNING):
        players = await get_spotify_media_players(mock_hass)

    assert players == []
    assert "No Spotify-capable media players found" in caplog.text


@pytest.mark.asyncio
async def test_no_supported_players_returns_empty_list(mock_hass, caplog):
    """Test empty list when no players support play_media."""
    mock_states = [
        create_mock_state(
            "media_player.basic_player", "idle", supported_features=0  # No support
        ),
    ]
    mock_hass.states.async_all.return_value = mock_states

    with caplog.at_level(logging.WARNING):
        players = await get_spotify_media_players(mock_hass)

    assert players == []
    assert "No Spotify-capable media players found" in caplog.text


@pytest.mark.asyncio
async def test_empty_list_does_not_raise_exception(mock_hass):
    """Test function does not raise exceptions on empty result."""
    mock_hass.states.async_all.return_value = []

    # Should not raise
    players = await get_spotify_media_players(mock_hass)
    assert players == []


# Test error handling (AC-3)


@pytest.mark.asyncio
async def test_exception_returns_empty_list(mock_hass, caplog):
    """Test exception in detection logic returns empty list."""
    mock_hass.states.async_all.side_effect = Exception("Test error")

    with caplog.at_level(logging.ERROR):
        players = await get_spotify_media_players(mock_hass)

    assert players == []
    assert "Error detecting media players" in caplog.text
    assert "Test error" in caplog.text


@pytest.mark.asyncio
async def test_none_attributes_handled_gracefully(mock_hass):
    """Test None attributes handled gracefully."""
    mock_state = Mock(spec=State)
    mock_state.entity_id = "media_player.cast_device"
    mock_state.state = "idle"
    mock_state.attributes = None  # None attributes

    mock_hass.states.async_all.return_value = [mock_state]

    # Should not raise
    players = await get_spotify_media_players(mock_hass)

    # Cast device should still be detected by entity_id
    assert len(players) == 1
    assert players[0].friendly_name == "media_player.cast_device"  # Fallback


# Test logging (AC-1, AC-3)


@pytest.mark.asyncio
async def test_info_log_on_success(mock_hass, caplog):
    """Test INFO log when players found."""
    mock_states = [
        create_mock_state("media_player.cast_1", "idle"),
        create_mock_state("media_player.cast_2", "idle"),
    ]
    mock_hass.states.async_all.return_value = mock_states

    with caplog.at_level(logging.INFO):
        await get_spotify_media_players(mock_hass)

    assert "Found 2 Spotify-capable media player(s)" in caplog.text


# Test integration with component (AC-5)


@pytest.mark.asyncio
async def test_returned_data_json_serializable(mock_hass):
    """Test returned data structure is suitable for API/JSON serialization."""
    mock_states = [
        create_mock_state("media_player.cast", "idle", "Test Cast", SUPPORT_PLAY_MEDIA),
    ]
    mock_hass.states.async_all.return_value = mock_states

    players = await get_spotify_media_players(mock_hass)

    # Verify player data can be converted to dict (for JSON)
    assert len(players) == 1
    player_dict = {
        "entity_id": players[0].entity_id,
        "friendly_name": players[0].friendly_name,
        "state": players[0].state,
        "supports_play_media": players[0].supports_play_media,
    }

    # Verify all values are JSON-serializable types
    assert isinstance(player_dict["entity_id"], str)
    assert isinstance(player_dict["friendly_name"], str)
    assert isinstance(player_dict["state"], str)
    assert isinstance(player_dict["supports_play_media"], bool)


@pytest.mark.asyncio
async def test_entity_id_valid_for_service_call(mock_hass):
    """Test entity_id format is valid for media_player.play_media service."""
    mock_states = [
        create_mock_state("media_player.test_speaker", "idle", "Test"),
    ]
    mock_hass.states.async_all.return_value = mock_states

    players = await get_spotify_media_players(mock_hass)

    # Verify entity_id format
    assert len(players) == 1
    assert players[0].entity_id.startswith("media_player.")
    assert "." in players[0].entity_id
    parts = players[0].entity_id.split(".")
    assert len(parts) == 2
    assert parts[0] == "media_player"
    assert len(parts[1]) > 0


# Test performance (AC-1)


@pytest.mark.asyncio
async def test_detection_completes_quickly(mock_hass):
    """Test detection completes within reasonable time (< 100ms target)."""
    import time

    # Create 10 mock players
    mock_states = [
        create_mock_state(f"media_player.cast_{i}", "idle", f"Cast {i}")
        for i in range(10)
    ]
    mock_hass.states.async_all.return_value = mock_states

    start = time.time()
    players = await get_spotify_media_players(mock_hass)
    duration = time.time() - start

    assert len(players) == 10
    # Should complete in well under 100ms for 10 players
    # Using 50ms as reasonable threshold for in-memory operations
    assert duration < 0.05  # 50ms
