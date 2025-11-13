"""Pytest configuration and fixtures for Beatsy tests.

This file provides global mocking for homeassistant modules that are imported
before tests can patch them.
"""
import sys
from unittest.mock import MagicMock, Mock

# Mock aiohttp before any imports
aiohttp_mock = MagicMock()
aiohttp_web_mock = MagicMock()
aiohttp_mock.web = aiohttp_web_mock
aiohttp_mock.WSMessage = MagicMock
aiohttp_mock.WSMsgType = MagicMock
sys.modules["aiohttp"] = aiohttp_mock

# Mock homeassistant modules before any imports
homeassistant_mock = MagicMock()
homeassistant_components_mock = MagicMock()
homeassistant_components_websocket_api_mock = MagicMock()
homeassistant_components_http_mock = MagicMock()
homeassistant_core_mock = MagicMock()
homeassistant_config_entries_mock = MagicMock()
homeassistant_helpers_mock = MagicMock()
homeassistant_helpers_storage_mock = MagicMock()

# Mock http component
homeassistant_components_http_mock.HomeAssistantView = MagicMock

# Create BASE_COMMAND_MESSAGE_SCHEMA mock
BASE_COMMAND_MESSAGE_SCHEMA_mock = MagicMock()
BASE_COMMAND_MESSAGE_SCHEMA_mock.extend = Mock(side_effect=lambda x: x)

# Set up websocket_api mocks
homeassistant_components_websocket_api_mock.BASE_COMMAND_MESSAGE_SCHEMA = (
    BASE_COMMAND_MESSAGE_SCHEMA_mock
)
homeassistant_components_websocket_api_mock.event_message = Mock(
    side_effect=lambda conn_id, msg: msg
)
homeassistant_components_websocket_api_mock.websocket_command = lambda schema: lambda func: func
homeassistant_components_websocket_api_mock.ActiveConnection = MagicMock
homeassistant_components_websocket_api_mock.async_register_command = Mock()

# Set up module hierarchy
homeassistant_components_mock.websocket_api = homeassistant_components_websocket_api_mock
homeassistant_components_mock.http = homeassistant_components_http_mock
homeassistant_mock.components = homeassistant_components_mock
homeassistant_mock.core = homeassistant_core_mock
homeassistant_mock.config_entries = homeassistant_config_entries_mock
homeassistant_mock.helpers = homeassistant_helpers_mock
homeassistant_helpers_mock.storage = homeassistant_helpers_storage_mock

# Mock core classes
homeassistant_core_mock.HomeAssistant = MagicMock
homeassistant_core_mock.callback = lambda func: func
homeassistant_config_entries_mock.ConfigEntry = MagicMock
homeassistant_helpers_storage_mock.Store = MagicMock

# Install mocks into sys.modules
sys.modules["homeassistant"] = homeassistant_mock
sys.modules["homeassistant.components"] = homeassistant_components_mock
sys.modules["homeassistant.components.websocket_api"] = (
    homeassistant_components_websocket_api_mock
)
sys.modules["homeassistant.components.http"] = homeassistant_components_http_mock
sys.modules["homeassistant.core"] = homeassistant_core_mock
sys.modules["homeassistant.config_entries"] = homeassistant_config_entries_mock
sys.modules["homeassistant.helpers"] = homeassistant_helpers_mock
sys.modules["homeassistant.helpers.storage"] = homeassistant_helpers_storage_mock
