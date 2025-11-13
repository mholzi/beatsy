"""Simplified unit tests for Beatsy lifecycle without full HA dependencies.

This test validates the core logic of the config entry lifecycle functions
using simple mocks, avoiding the need for the full pytest-homeassistant setup.
"""
from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, Mock, call
import sys
from pathlib import Path

# Add the custom_components directory to the path
sys.path.insert(
    0, str(Path(__file__).parent.parent / "home-assistant-config" / "custom_components")
)


def test_imports():
    """Test that all modules can be imported successfully."""
    # Test config flow import
    from beatsy.config_flow import BeatsyConfigFlow
    from beatsy.const import DOMAIN

    assert DOMAIN == "beatsy"
    assert BeatsyConfigFlow.VERSION == 1
    print("✓ Config flow imports successful")


def test_const_values():
    """Test that constants are correctly defined."""
    from beatsy.const import DOMAIN

    assert DOMAIN == "beatsy"
    print("✓ Constants validated")


async def test_async_setup_entry_basic():
    """Test basic async_setup_entry functionality."""
    from beatsy import async_setup_entry, DOMAIN

    # Create minimal mocks
    mock_hass = Mock()
    mock_hass.data = {}
    mock_hass.config_entries = Mock()
    mock_hass.http = Mock()
    mock_hass.services = Mock()

    # Mock async methods
    mock_hass.config_entries.async_forward_entry_setups = AsyncMock(return_value=True)
    mock_hass.config_entries.async_entries = Mock(return_value=[])
    mock_hass.http.register_view = Mock()
    mock_hass.services.async_register = Mock()

    mock_entry = Mock()
    mock_entry.entry_id = "test_entry"
    mock_entry.data = {}

    # Run setup
    result = await async_setup_entry(mock_hass, mock_entry)

    # Validate
    assert result is True
    assert DOMAIN in mock_hass.data
    assert mock_entry.entry_id in mock_hass.data[DOMAIN]

    entry_data = mock_hass.data[DOMAIN][mock_entry.entry_id]
    assert "game_config" in entry_data
    assert "players" in entry_data
    assert "current_round" in entry_data
    assert "played_songs" in entry_data
    assert "available_songs" in entry_data
    assert "websocket_connections" in entry_data

    print("✓ async_setup_entry creates proper state structure")


async def test_async_unload_entry_basic():
    """Test basic async_unload_entry functionality."""
    from beatsy import async_setup_entry, async_unload_entry, DOMAIN

    # Setup
    mock_hass = Mock()
    mock_hass.data = {}
    mock_hass.config_entries = Mock()
    mock_hass.http = Mock()
    mock_hass.services = Mock()

    mock_hass.config_entries.async_forward_entry_setups = AsyncMock(return_value=True)
    mock_hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)
    mock_hass.config_entries.async_entries = Mock(return_value=[])
    mock_hass.http.register_view = Mock()
    mock_hass.services.async_register = Mock()

    mock_entry = Mock()
    mock_entry.entry_id = "test_entry"
    mock_entry.data = {}

    # Setup entry
    await async_setup_entry(mock_hass, mock_entry)
    assert mock_entry.entry_id in mock_hass.data[DOMAIN]

    # Unload entry
    result = await async_unload_entry(mock_hass, mock_entry)

    # Validate
    assert result is True
    assert mock_entry.entry_id not in mock_hass.data[DOMAIN]

    print("✓ async_unload_entry removes entry data")


async def test_async_reload_entry_basic():
    """Test basic async_reload_entry functionality."""
    from beatsy import async_setup_entry, async_reload_entry, DOMAIN

    # Setup
    mock_hass = Mock()
    mock_hass.data = {}
    mock_hass.config_entries = Mock()
    mock_hass.http = Mock()
    mock_hass.services = Mock()

    mock_hass.config_entries.async_forward_entry_setups = AsyncMock(return_value=True)
    mock_hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)
    mock_hass.config_entries.async_entries = Mock(return_value=[])
    mock_hass.http.register_view = Mock()
    mock_hass.services.async_register = Mock()

    mock_entry = Mock()
    mock_entry.entry_id = "test_entry"
    mock_entry.data = {}

    # Setup entry
    await async_setup_entry(mock_hass, mock_entry)

    # Add some data
    mock_hass.data[DOMAIN][mock_entry.entry_id]["players"].append({"name": "Alice"})

    # Reload entry
    await async_reload_entry(mock_hass, mock_entry)

    # Validate - state should be reset
    assert mock_entry.entry_id in mock_hass.data[DOMAIN]
    assert mock_hass.data[DOMAIN][mock_entry.entry_id]["players"] == []

    print("✓ async_reload_entry resets state")


async def test_websocket_cleanup():
    """Test that WebSocket connections are closed on unload."""
    from beatsy import async_setup_entry, async_unload_entry, DOMAIN

    # Setup
    mock_hass = Mock()
    mock_hass.data = {}
    mock_hass.config_entries = Mock()
    mock_hass.http = Mock()
    mock_hass.services = Mock()

    mock_hass.config_entries.async_forward_entry_setups = AsyncMock(return_value=True)
    mock_hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)
    mock_hass.config_entries.async_entries = Mock(return_value=[])
    mock_hass.http.register_view = Mock()
    mock_hass.services.async_register = Mock()

    mock_entry = Mock()
    mock_entry.entry_id = "test_entry"
    mock_entry.data = {}

    # Setup entry
    await async_setup_entry(mock_hass, mock_entry)

    # Add mock WebSocket connection
    mock_conn = Mock()
    mock_conn.close = AsyncMock()
    mock_hass.data[DOMAIN][mock_entry.entry_id]["websocket_connections"]["conn1"] = (
        mock_conn
    )

    # Unload
    await async_unload_entry(mock_hass, mock_entry)

    # Verify connection was closed
    mock_conn.close.assert_called_once()

    print("✓ WebSocket connections are closed on unload")


async def test_config_flow_basic():
    """Test basic config flow functionality."""
    from beatsy.config_flow import BeatsyConfigFlow

    flow = BeatsyConfigFlow()
    flow.hass = Mock()

    # Test initial step
    result = await flow.async_step_user(user_input=None)

    # Should show form
    assert result["type"] == "form"
    assert result["step_id"] == "user"

    print("✓ Config flow shows form on initial step")


def run_async_test(test_func):
    """Helper to run async tests."""
    asyncio.run(test_func())


if __name__ == "__main__":
    print("\nRunning Beatsy Component Lifecycle Tests")
    print("=" * 60)

    # Run synchronous tests
    test_imports()
    test_const_values()

    # Run async tests
    run_async_test(test_async_setup_entry_basic)
    run_async_test(test_async_unload_entry_basic)
    run_async_test(test_async_reload_entry_basic)
    run_async_test(test_websocket_cleanup)
    run_async_test(test_config_flow_basic)

    print("=" * 60)
    print("✅ All tests passed!")
    print()
