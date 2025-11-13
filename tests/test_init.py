"""Unit tests for Beatsy component initialization and lifecycle."""
from __future__ import annotations

from unittest.mock import AsyncMock, Mock, patch

import pytest

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

# Import the module under test
import sys
from pathlib import Path

# Add the custom_components directory to the path
sys.path.insert(
    0, str(Path(__file__).parent.parent / "home-assistant-config" / "custom_components")
)

from beatsy import (
    DOMAIN,
    PLATFORMS,
    async_reload_entry,
    async_setup_entry,
    async_unload_entry,
)


@pytest.fixture
def mock_hass():
    """Create a mock HomeAssistant instance."""
    hass = Mock(spec=HomeAssistant)
    hass.data = {}
    hass.config_entries = Mock()
    hass.http = Mock()
    hass.services = Mock()

    # Mock async methods
    hass.config_entries.async_forward_entry_setups = AsyncMock(return_value=True)
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)
    hass.config_entries.async_entries = Mock(return_value=[])
    hass.http.register_view = Mock()
    hass.services.async_register = Mock()

    return hass


@pytest.fixture
def mock_config_entry():
    """Create a mock ConfigEntry."""
    entry = Mock(spec=ConfigEntry)
    entry.entry_id = "test_entry_id"
    entry.data = {}
    return entry


class TestAsyncSetupEntry:
    """Tests for async_setup_entry function."""

    @pytest.mark.asyncio
    async def test_async_setup_entry_returns_true(
        self, mock_hass, mock_config_entry
    ):
        """Test that async_setup_entry returns True on success."""
        result = await async_setup_entry(mock_hass, mock_config_entry)
        assert result is True

    @pytest.mark.asyncio
    async def test_async_setup_entry_initializes_domain_data(
        self, mock_hass, mock_config_entry
    ):
        """Test that async_setup_entry initializes hass.data[DOMAIN]."""
        await async_setup_entry(mock_hass, mock_config_entry)
        assert DOMAIN in mock_hass.data

    @pytest.mark.asyncio
    async def test_async_setup_entry_initializes_entry_data(
        self, mock_hass, mock_config_entry
    ):
        """Test that async_setup_entry initializes per-entry state."""
        await async_setup_entry(mock_hass, mock_config_entry)

        assert mock_config_entry.entry_id in mock_hass.data[DOMAIN]
        entry_data = mock_hass.data[DOMAIN][mock_config_entry.entry_id]

        # Verify all required keys are present
        assert "game_config" in entry_data
        assert "players" in entry_data
        assert "current_round" in entry_data
        assert "played_songs" in entry_data
        assert "available_songs" in entry_data
        assert "websocket_connections" in entry_data
        assert "spotify" in entry_data

    @pytest.mark.asyncio
    async def test_async_setup_entry_initializes_state_structure(
        self, mock_hass, mock_config_entry
    ):
        """Test that async_setup_entry creates correct state structure."""
        await async_setup_entry(mock_hass, mock_config_entry)

        entry_data = mock_hass.data[DOMAIN][mock_config_entry.entry_id]

        # Verify structure types
        assert isinstance(entry_data["game_config"], dict)
        assert isinstance(entry_data["players"], list)
        assert entry_data["current_round"] is None
        assert isinstance(entry_data["played_songs"], list)
        assert isinstance(entry_data["available_songs"], list)
        assert isinstance(entry_data["websocket_connections"], dict)

    @pytest.mark.asyncio
    async def test_async_setup_entry_calls_forward_entry_setups(
        self, mock_hass, mock_config_entry
    ):
        """Test that async_setup_entry calls async_forward_entry_setups."""
        await async_setup_entry(mock_hass, mock_config_entry)

        mock_hass.config_entries.async_forward_entry_setups.assert_called_once_with(
            mock_config_entry, PLATFORMS
        )

    @pytest.mark.asyncio
    async def test_async_setup_entry_forwards_empty_platforms(
        self, mock_hass, mock_config_entry
    ):
        """Test that async_setup_entry forwards empty PLATFORMS list."""
        await async_setup_entry(mock_hass, mock_config_entry)

        # Verify PLATFORMS is empty as per story requirements
        assert PLATFORMS == []

        mock_hass.config_entries.async_forward_entry_setups.assert_called_once_with(
            mock_config_entry, []
        )

    @pytest.mark.asyncio
    async def test_async_setup_entry_registers_http_view(
        self, mock_hass, mock_config_entry
    ):
        """Test that async_setup_entry registers HTTP view."""
        await async_setup_entry(mock_hass, mock_config_entry)

        # Should register at least 2 views (HTTP test view + WebSocket)
        assert mock_hass.http.register_view.call_count >= 2

    @pytest.mark.asyncio
    async def test_async_setup_entry_registers_service(
        self, mock_hass, mock_config_entry
    ):
        """Test that async_setup_entry registers test service."""
        await async_setup_entry(mock_hass, mock_config_entry)

        mock_hass.services.async_register.assert_called_once()
        args = mock_hass.services.async_register.call_args[0]
        assert args[0] == DOMAIN
        assert args[1] == "test_fetch_playlist"

    @pytest.mark.asyncio
    async def test_async_setup_entry_http_view_failure_returns_false(
        self, mock_hass, mock_config_entry
    ):
        """Test that async_setup_entry returns False on HTTP view registration failure."""
        mock_hass.http.register_view.side_effect = Exception("Registration failed")

        result = await async_setup_entry(mock_hass, mock_config_entry)
        assert result is False


class TestAsyncUnloadEntry:
    """Tests for async_unload_entry function."""

    @pytest.mark.asyncio
    async def test_async_unload_entry_calls_unload_platforms(
        self, mock_hass, mock_config_entry
    ):
        """Test that async_unload_entry calls async_unload_platforms."""
        # Setup entry first
        await async_setup_entry(mock_hass, mock_config_entry)

        # Unload
        await async_unload_entry(mock_hass, mock_config_entry)

        mock_hass.config_entries.async_unload_platforms.assert_called_once_with(
            mock_config_entry, PLATFORMS
        )

    @pytest.mark.asyncio
    async def test_async_unload_entry_removes_entry_data(
        self, mock_hass, mock_config_entry
    ):
        """Test that async_unload_entry removes entry-specific state."""
        # Setup entry
        await async_setup_entry(mock_hass, mock_config_entry)
        assert mock_config_entry.entry_id in mock_hass.data[DOMAIN]

        # Unload entry
        result = await async_unload_entry(mock_hass, mock_config_entry)

        # Verify entry data removed
        assert result is True
        assert mock_config_entry.entry_id not in mock_hass.data[DOMAIN]

    @pytest.mark.asyncio
    async def test_async_unload_entry_returns_true_on_success(
        self, mock_hass, mock_config_entry
    ):
        """Test that async_unload_entry returns True on successful unload."""
        await async_setup_entry(mock_hass, mock_config_entry)

        result = await async_unload_entry(mock_hass, mock_config_entry)
        assert result is True

    @pytest.mark.asyncio
    async def test_async_unload_entry_closes_websocket_connections(
        self, mock_hass, mock_config_entry
    ):
        """Test that async_unload_entry closes WebSocket connections."""
        # Setup entry
        await async_setup_entry(mock_hass, mock_config_entry)

        # Add mock connections
        mock_conn1 = Mock()
        mock_conn1.close = AsyncMock()
        mock_conn2 = Mock()
        mock_conn2.close = AsyncMock()

        mock_hass.data[DOMAIN][mock_config_entry.entry_id]["websocket_connections"] = {
            "conn1": mock_conn1,
            "conn2": mock_conn2,
        }

        # Unload
        await async_unload_entry(mock_hass, mock_config_entry)

        # Verify connections closed
        mock_conn1.close.assert_called_once()
        mock_conn2.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_unload_entry_handles_missing_websocket_connections(
        self, mock_hass, mock_config_entry
    ):
        """Test that async_unload_entry handles missing websocket_connections gracefully."""
        # Setup entry
        await async_setup_entry(mock_hass, mock_config_entry)

        # Remove websocket_connections key
        del mock_hass.data[DOMAIN][mock_config_entry.entry_id]["websocket_connections"]

        # Should not raise exception
        result = await async_unload_entry(mock_hass, mock_config_entry)
        assert result is True

    @pytest.mark.asyncio
    async def test_async_unload_entry_returns_false_when_platforms_fail(
        self, mock_hass, mock_config_entry
    ):
        """Test that async_unload_entry returns False when platform unload fails."""
        await async_setup_entry(mock_hass, mock_config_entry)

        # Make platform unload fail
        mock_hass.config_entries.async_unload_platforms.return_value = False

        result = await async_unload_entry(mock_hass, mock_config_entry)
        assert result is False


class TestAsyncReloadEntry:
    """Tests for async_reload_entry function."""

    @pytest.mark.asyncio
    async def test_async_reload_entry_unloads_then_reloads(
        self, mock_hass, mock_config_entry
    ):
        """Test that async_reload_entry unloads and then reloads."""
        # Setup entry
        await async_setup_entry(mock_hass, mock_config_entry)

        # Add some data to verify it gets reset
        mock_hass.data[DOMAIN][mock_config_entry.entry_id]["players"].append(
            {"name": "test_player"}
        )

        # Reload
        await async_reload_entry(mock_hass, mock_config_entry)

        # Verify state was reinitialized (players list should be empty again)
        assert mock_hass.data[DOMAIN][mock_config_entry.entry_id]["players"] == []

    @pytest.mark.asyncio
    async def test_async_reload_entry_maintains_entry_in_data(
        self, mock_hass, mock_config_entry
    ):
        """Test that async_reload_entry keeps entry in hass.data."""
        await async_setup_entry(mock_hass, mock_config_entry)

        await async_reload_entry(mock_hass, mock_config_entry)

        # Entry should still exist
        assert mock_config_entry.entry_id in mock_hass.data[DOMAIN]

    @pytest.mark.asyncio
    async def test_async_reload_entry_reinitializes_all_state_keys(
        self, mock_hass, mock_config_entry
    ):
        """Test that async_reload_entry reinitializes all required state keys."""
        await async_setup_entry(mock_hass, mock_config_entry)

        await async_reload_entry(mock_hass, mock_config_entry)

        entry_data = mock_hass.data[DOMAIN][mock_config_entry.entry_id]

        # Verify all keys exist
        assert "game_config" in entry_data
        assert "players" in entry_data
        assert "current_round" in entry_data
        assert "played_songs" in entry_data
        assert "available_songs" in entry_data
        assert "websocket_connections" in entry_data


class TestMultipleInstances:
    """Tests for multi-instance support via per-entry state."""

    @pytest.mark.asyncio
    async def test_multiple_entries_independent_state(self, mock_hass):
        """Test that multiple config entries have independent state."""
        # Create two entries
        entry1 = Mock(spec=ConfigEntry)
        entry1.entry_id = "entry_1"
        entry1.data = {}

        entry2 = Mock(spec=ConfigEntry)
        entry2.entry_id = "entry_2"
        entry2.data = {}

        # Mock the HA methods for both entries
        mock_hass.config_entries = Mock()
        mock_hass.http = Mock()
        mock_hass.services = Mock()
        mock_hass.config_entries.async_forward_entry_setups = AsyncMock(return_value=True)
        mock_hass.config_entries.async_entries = Mock(return_value=[])
        mock_hass.http.register_view = Mock()
        mock_hass.services.async_register = Mock()

        # Setup both entries
        await async_setup_entry(mock_hass, entry1)
        await async_setup_entry(mock_hass, entry2)

        # Verify both exist
        assert entry1.entry_id in mock_hass.data[DOMAIN]
        assert entry2.entry_id in mock_hass.data[DOMAIN]

        # Modify one entry's state
        mock_hass.data[DOMAIN][entry1.entry_id]["players"].append({"name": "player1"})

        # Verify other entry's state is independent
        assert len(mock_hass.data[DOMAIN][entry1.entry_id]["players"]) == 1
        assert len(mock_hass.data[DOMAIN][entry2.entry_id]["players"]) == 0

    @pytest.mark.asyncio
    async def test_unload_one_entry_leaves_other_intact(self, mock_hass):
        """Test that unloading one entry doesn't affect other entries."""
        # Create two entries
        entry1 = Mock(spec=ConfigEntry)
        entry1.entry_id = "entry_1"
        entry1.data = {}

        entry2 = Mock(spec=ConfigEntry)
        entry2.entry_id = "entry_2"
        entry2.data = {}

        # Mock the HA methods
        mock_hass.config_entries = Mock()
        mock_hass.http = Mock()
        mock_hass.services = Mock()
        mock_hass.config_entries.async_forward_entry_setups = AsyncMock(return_value=True)
        mock_hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)
        mock_hass.config_entries.async_entries = Mock(return_value=[])
        mock_hass.http.register_view = Mock()
        mock_hass.services.async_register = Mock()

        # Setup both entries
        await async_setup_entry(mock_hass, entry1)
        await async_setup_entry(mock_hass, entry2)

        # Unload entry1
        await async_unload_entry(mock_hass, entry1)

        # Verify entry1 removed but entry2 remains
        assert entry1.entry_id not in mock_hass.data[DOMAIN]
        assert entry2.entry_id in mock_hass.data[DOMAIN]
