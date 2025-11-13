"""Integration tests for complete Beatsy config entry lifecycle.

This test file validates the full lifecycle from config flow through setup,
reload, and unload operations.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, Mock

import pytest

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant import data_entry_flow

# Import the modules under test
import sys
from pathlib import Path

# Add the custom_components directory to the path
sys.path.insert(
    0, str(Path(__file__).parent.parent / "home-assistant-config" / "custom_components")
)

from beatsy import (
    DOMAIN,
    async_reload_entry,
    async_setup_entry,
    async_unload_entry,
)
from beatsy.config_flow import BeatsyConfigFlow


@pytest.fixture
def mock_hass():
    """Create a comprehensive mock HomeAssistant instance."""
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
    entry.entry_id = "test_integration_entry"
    entry.data = {}
    return entry


class TestFullConfigEntryLifecycle:
    """Integration tests for complete config entry lifecycle."""

    @pytest.mark.asyncio
    async def test_complete_lifecycle_flow(self, mock_hass, mock_config_entry):
        """Test complete lifecycle: config flow → setup → reload → unload.

        This validates AC: #1, #3, #4, #5
        """
        # Phase 1: Config Flow (AC: #5)
        flow = BeatsyConfigFlow()
        flow.hass = mock_hass

        # Show initial form
        result = await flow.async_step_user(user_input=None)
        assert result["type"] == data_entry_flow.FlowResultType.FORM
        assert result["step_id"] == "user"

        # Create entry
        def mock_create_entry(title, data):
            return {
                "type": data_entry_flow.FlowResultType.CREATE_ENTRY,
                "title": title,
                "data": data,
                "result": mock_config_entry,
            }

        flow.async_create_entry = mock_create_entry
        result = await flow.async_step_user(user_input={})
        assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY

        # Phase 2: Setup (AC: #1)
        setup_result = await async_setup_entry(mock_hass, mock_config_entry)
        assert setup_result is True
        assert mock_config_entry.entry_id in mock_hass.data[DOMAIN]

        # Verify state initialized
        entry_data = mock_hass.data[DOMAIN][mock_config_entry.entry_id]
        assert "game_config" in entry_data
        assert "players" in entry_data
        assert "current_round" in entry_data
        assert "played_songs" in entry_data
        assert "available_songs" in entry_data
        assert "websocket_connections" in entry_data

        # Phase 3: Simulate usage - add some state
        entry_data["players"].append({"name": "Alice", "score": 10})
        entry_data["played_songs"].append("spotify:track:123")

        # Phase 4: Reload (AC: #3)
        await async_reload_entry(mock_hass, mock_config_entry)

        # Verify state was reset
        entry_data_after_reload = mock_hass.data[DOMAIN][mock_config_entry.entry_id]
        assert entry_data_after_reload["players"] == []
        assert entry_data_after_reload["played_songs"] == []
        assert mock_config_entry.entry_id in mock_hass.data[DOMAIN]

        # Phase 5: Unload (AC: #4)
        unload_result = await async_unload_entry(mock_hass, mock_config_entry)
        assert unload_result is True
        assert mock_config_entry.entry_id not in mock_hass.data[DOMAIN]

    @pytest.mark.asyncio
    async def test_setup_creates_required_state_structure(
        self, mock_hass, mock_config_entry
    ):
        """Test that setup creates all required state keys (AC: #1)."""
        await async_setup_entry(mock_hass, mock_config_entry)

        entry_data = mock_hass.data[DOMAIN][mock_config_entry.entry_id]

        # Verify all keys from state structure
        required_keys = [
            "game_config",
            "players",
            "current_round",
            "played_songs",
            "available_songs",
            "websocket_connections",
        ]

        for key in required_keys:
            assert key in entry_data, f"Missing required state key: {key}"

    @pytest.mark.asyncio
    async def test_reload_preserves_entry_id(self, mock_hass, mock_config_entry):
        """Test that reload maintains the same entry ID (AC: #3)."""
        await async_setup_entry(mock_hass, mock_config_entry)
        original_entry_id = mock_config_entry.entry_id

        await async_reload_entry(mock_hass, mock_config_entry)

        assert mock_config_entry.entry_id == original_entry_id
        assert original_entry_id in mock_hass.data[DOMAIN]

    @pytest.mark.asyncio
    async def test_reload_cleans_up_resources(self, mock_hass, mock_config_entry):
        """Test that reload closes connections and cancels tasks (AC: #3)."""
        await async_setup_entry(mock_hass, mock_config_entry)

        # Add mock WebSocket connection
        mock_conn = Mock()
        mock_conn.close = AsyncMock()
        mock_hass.data[DOMAIN][mock_config_entry.entry_id]["websocket_connections"] = {
            "test_conn": mock_conn
        }

        # Reload should close the connection
        await async_reload_entry(mock_hass, mock_config_entry)

        # Verify connection was closed
        mock_conn.close.assert_called()

    @pytest.mark.asyncio
    async def test_unload_removes_all_entry_data(self, mock_hass, mock_config_entry):
        """Test that unload completely removes entry data (AC: #4)."""
        await async_setup_entry(mock_hass, mock_config_entry)

        # Populate some data
        entry_data = mock_hass.data[DOMAIN][mock_config_entry.entry_id]
        entry_data["game_config"]["test"] = "value"
        entry_data["players"].append({"name": "Bob"})

        # Unload
        await async_unload_entry(mock_hass, mock_config_entry)

        # Verify complete removal
        assert mock_config_entry.entry_id not in mock_hass.data.get(DOMAIN, {})

    @pytest.mark.asyncio
    async def test_unload_closes_websocket_connections(
        self, mock_hass, mock_config_entry
    ):
        """Test that unload closes all WebSocket connections (AC: #4)."""
        await async_setup_entry(mock_hass, mock_config_entry)

        # Create multiple mock connections
        mock_conn1 = Mock()
        mock_conn1.close = AsyncMock()
        mock_conn2 = Mock()
        mock_conn2.close = AsyncMock()
        mock_conn3 = Mock()
        mock_conn3.close = AsyncMock()

        mock_hass.data[DOMAIN][mock_config_entry.entry_id]["websocket_connections"] = {
            "conn1": mock_conn1,
            "conn2": mock_conn2,
            "conn3": mock_conn3,
        }

        # Unload
        await async_unload_entry(mock_hass, mock_config_entry)

        # Verify all connections closed
        mock_conn1.close.assert_called_once()
        mock_conn2.close.assert_called_once()
        mock_conn3.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_unload_calls_platform_unload(self, mock_hass, mock_config_entry):
        """Test that unload calls async_unload_platforms first (AC: #4)."""
        await async_setup_entry(mock_hass, mock_config_entry)

        await async_unload_entry(mock_hass, mock_config_entry)

        # Verify platform unload was called
        mock_hass.config_entries.async_unload_platforms.assert_called()

    @pytest.mark.asyncio
    async def test_config_flow_to_setup_integration(self, mock_hass):
        """Test seamless flow from config entry creation to setup (AC: #5, #1)."""
        # Create config entry via flow
        flow = BeatsyConfigFlow()
        flow.hass = mock_hass

        entry = Mock(spec=ConfigEntry)
        entry.entry_id = "flow_test_entry"
        entry.data = {}

        def mock_create_entry(title, data):
            return {
                "type": data_entry_flow.FlowResultType.CREATE_ENTRY,
                "title": title,
                "data": data,
                "result": entry,
            }

        flow.async_create_entry = mock_create_entry
        flow_result = await flow.async_step_user(user_input={})

        # Verify entry created
        assert flow_result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
        assert flow_result["title"] == "Beatsy"

        # Setup the entry
        setup_result = await async_setup_entry(mock_hass, entry)
        assert setup_result is True
        assert entry.entry_id in mock_hass.data[DOMAIN]


class TestMultipleEntriesLifecycle:
    """Test lifecycle with multiple concurrent config entries."""

    @pytest.mark.asyncio
    async def test_multiple_entries_independent_lifecycle(self, mock_hass):
        """Test that multiple entries can be managed independently."""
        # Create two entries
        entry1 = Mock(spec=ConfigEntry)
        entry1.entry_id = "multi_entry_1"
        entry1.data = {}

        entry2 = Mock(spec=ConfigEntry)
        entry2.entry_id = "multi_entry_2"
        entry2.data = {}

        # Mock HA methods
        mock_hass.config_entries = Mock()
        mock_hass.http = Mock()
        mock_hass.services = Mock()
        mock_hass.config_entries.async_forward_entry_setups = AsyncMock(return_value=True)
        mock_hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)
        mock_hass.config_entries.async_entries = Mock(return_value=[])
        mock_hass.http.register_view = Mock()
        mock_hass.services.async_register = Mock()

        # Setup both
        await async_setup_entry(mock_hass, entry1)
        await async_setup_entry(mock_hass, entry2)

        # Verify both exist
        assert entry1.entry_id in mock_hass.data[DOMAIN]
        assert entry2.entry_id in mock_hass.data[DOMAIN]

        # Reload entry1
        await async_reload_entry(mock_hass, entry1)

        # Both should still exist
        assert entry1.entry_id in mock_hass.data[DOMAIN]
        assert entry2.entry_id in mock_hass.data[DOMAIN]

        # Unload entry1
        await async_unload_entry(mock_hass, entry1)

        # Entry1 gone, entry2 remains
        assert entry1.entry_id not in mock_hass.data[DOMAIN]
        assert entry2.entry_id in mock_hass.data[DOMAIN]

        # Unload entry2
        await async_unload_entry(mock_hass, entry2)

        # Both gone
        assert entry1.entry_id not in mock_hass.data.get(DOMAIN, {})
        assert entry2.entry_id not in mock_hass.data.get(DOMAIN, {})


class TestErrorHandling:
    """Test error handling in lifecycle operations."""

    @pytest.mark.asyncio
    async def test_unload_handles_platform_failure(self, mock_hass, mock_config_entry):
        """Test that unload handles platform unload failures gracefully."""
        await async_setup_entry(mock_hass, mock_config_entry)

        # Make platform unload fail
        mock_hass.config_entries.async_unload_platforms.return_value = False

        result = await async_unload_entry(mock_hass, mock_config_entry)

        # Should return False but not crash
        assert result is False

    @pytest.mark.asyncio
    async def test_setup_handles_http_view_failure(self, mock_hass, mock_config_entry):
        """Test that setup handles HTTP view registration failures."""
        mock_hass.http.register_view.side_effect = Exception("View registration failed")

        result = await async_setup_entry(mock_hass, mock_config_entry)

        # Should return False on view registration failure
        assert result is False

    @pytest.mark.asyncio
    async def test_unload_handles_missing_websocket_connections(
        self, mock_hass, mock_config_entry
    ):
        """Test that unload doesn't crash if websocket_connections is missing."""
        await async_setup_entry(mock_hass, mock_config_entry)

        # Remove websocket_connections
        del mock_hass.data[DOMAIN][mock_config_entry.entry_id]["websocket_connections"]

        # Should not raise exception
        result = await async_unload_entry(mock_hass, mock_config_entry)
        assert result is True
