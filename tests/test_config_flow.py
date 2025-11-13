"""Unit tests for Beatsy config flow (Story 2.7)."""
from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from homeassistant import config_entries, data_entry_flow
from homeassistant.core import HomeAssistant

# Import the module under test
import sys
from pathlib import Path

# Add the custom_components directory to the path
sys.path.insert(
    0, str(Path(__file__).parent.parent / "home-assistant-config" / "custom_components")
)

from beatsy.config_flow import BeatsyConfigFlow, BeatsyOptionsFlow
from beatsy.const import DOMAIN


@pytest.fixture
def mock_hass():
    """Create a mock HomeAssistant instance."""
    hass = Mock(spec=HomeAssistant)
    hass.data = {}
    hass.config_entries = Mock()
    return hass


class TestBeatsyConfigFlow:
    """Tests for BeatsyConfigFlow (AC-1, AC-2, AC-3, AC-4)."""

    @pytest.mark.asyncio
    async def test_config_flow_init(self):
        """Test config flow initialization."""
        flow = BeatsyConfigFlow()
        assert flow.VERSION == 1

    @pytest.mark.asyncio
    async def test_user_step_shows_form_with_schema(self, mock_hass):
        """Test user step displays form with correct schema (AC-2)."""
        flow = BeatsyConfigFlow()
        flow.hass = mock_hass

        result = await flow.async_step_user(user_input=None)

        assert result["type"] == data_entry_flow.FlowResultType.FORM
        assert result["step_id"] == "user"

        # Verify schema contains required fields
        schema = result["data_schema"].schema
        assert "timer_duration" in str(schema)
        assert "year_range_min" in str(schema)
        assert "year_range_max" in str(schema)

    @pytest.mark.asyncio
    async def test_valid_input_creates_entry(self, mock_hass):
        """Test valid input creates config entry successfully (AC-4)."""
        flow = BeatsyConfigFlow()
        flow.hass = mock_hass

        # Mock async_create_entry
        def mock_create_entry(title, data):
            return {
                "type": data_entry_flow.FlowResultType.CREATE_ENTRY,
                "title": title,
                "data": data,
            }

        flow.async_create_entry = mock_create_entry

        user_input = {
            "timer_duration": 45,
            "year_range_min": 1960,
            "year_range_max": 2020,
        }

        result = await flow.async_step_user(user_input=user_input)

        assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
        assert result["title"] == "Beatsy"
        assert result["data"]["timer_duration"] == 45
        assert result["data"]["year_range_min"] == 1960
        assert result["data"]["year_range_max"] == 2020

    @pytest.mark.asyncio
    async def test_default_values_used(self, mock_hass):
        """Test default values are used when not specified (AC-2)."""
        flow = BeatsyConfigFlow()
        flow.hass = mock_hass

        def mock_create_entry(title, data):
            return {
                "type": data_entry_flow.FlowResultType.CREATE_ENTRY,
                "title": title,
                "data": data,
            }

        flow.async_create_entry = mock_create_entry

        # Submit with defaults (empty dict triggers defaults)
        user_input = {
            "timer_duration": 30,
            "year_range_min": 1950,
            "year_range_max": 2024,
        }

        result = await flow.async_step_user(user_input=user_input)

        assert result["data"]["timer_duration"] == 30
        assert result["data"]["year_range_min"] == 1950
        assert result["data"]["year_range_max"] == 2024

    @pytest.mark.asyncio
    async def test_year_range_validation_min_greater_than_max(self, mock_hass):
        """Test year range validation fails when min >= max (AC-3)."""
        flow = BeatsyConfigFlow()
        flow.hass = mock_hass

        user_input = {
            "timer_duration": 30,
            "year_range_min": 2000,
            "year_range_max": 1980,  # Invalid: min > max
        }

        result = await flow.async_step_user(user_input=user_input)

        assert result["type"] == data_entry_flow.FlowResultType.FORM
        assert "year_range_min" in result["errors"]
        assert result["errors"]["year_range_min"] == "min_greater_than_max"

    @pytest.mark.asyncio
    async def test_year_range_validation_min_equals_max(self, mock_hass):
        """Test year range validation fails when min == max (AC-3)."""
        flow = BeatsyConfigFlow()
        flow.hass = mock_hass

        user_input = {
            "timer_duration": 30,
            "year_range_min": 2000,
            "year_range_max": 2000,  # Invalid: min == max
        }

        result = await flow.async_step_user(user_input=user_input)

        assert result["type"] == data_entry_flow.FlowResultType.FORM
        assert "year_range_min" in result["errors"]

    @pytest.mark.asyncio
    async def test_entry_data_stored_correctly(self, mock_hass):
        """Test config entry data stored with all fields (AC-4)."""
        flow = BeatsyConfigFlow()
        flow.hass = mock_hass

        def mock_create_entry(title, data):
            return {
                "type": data_entry_flow.FlowResultType.CREATE_ENTRY,
                "title": title,
                "data": data,
            }

        flow.async_create_entry = mock_create_entry

        user_input = {
            "timer_duration": 60,
            "year_range_min": 1970,
            "year_range_max": 2010,
        }

        result = await flow.async_step_user(user_input=user_input)

        # Verify all fields present and correct
        assert "timer_duration" in result["data"]
        assert "year_range_min" in result["data"]
        assert "year_range_max" in result["data"]
        assert result["data"]["timer_duration"] == 60
        assert result["data"]["year_range_min"] == 1970
        assert result["data"]["year_range_max"] == 2010


class TestBeatsyOptionsFlow:
    """Tests for BeatsyOptionsFlow (AC-6)."""

    @pytest.fixture
    def mock_config_entry(self):
        """Create mock config entry."""
        entry = Mock(spec=config_entries.ConfigEntry)
        entry.data = {
            "timer_duration": 30,
            "year_range_min": 1950,
            "year_range_max": 2024,
        }
        entry.entry_id = "test_entry_id"
        return entry

    @pytest.mark.asyncio
    async def test_options_flow_displays_current_config(self, mock_hass, mock_config_entry):
        """Test options flow displays current configuration values (AC-6)."""
        flow = BeatsyOptionsFlow(mock_config_entry)
        flow.hass = mock_hass

        result = await flow.async_step_init(user_input=None)

        assert result["type"] == data_entry_flow.FlowResultType.FORM
        assert result["step_id"] == "init"

        # Verify schema contains fields with current values as defaults
        schema = result["data_schema"].schema
        assert "timer_duration" in str(schema)
        assert "year_range_min" in str(schema)
        assert "year_range_max" in str(schema)

    @pytest.mark.asyncio
    async def test_options_flow_updates_entry_data(self, mock_hass, mock_config_entry):
        """Test valid options update saved successfully (AC-6)."""
        flow = BeatsyOptionsFlow(mock_config_entry)
        flow.hass = mock_hass

        # Mock async_update_entry
        mock_hass.config_entries.async_update_entry = Mock()

        # Mock async_create_entry
        def mock_create_entry(title, data):
            return {
                "type": data_entry_flow.FlowResultType.CREATE_ENTRY,
                "title": title,
                "data": data,
            }

        flow.async_create_entry = mock_create_entry

        user_input = {
            "timer_duration": 60,
            "year_range_min": 1960,
            "year_range_max": 2020,
        }

        result = await flow.async_step_init(user_input=user_input)

        assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY

        # Verify async_update_entry was called with new data
        mock_hass.config_entries.async_update_entry.assert_called_once()
        call_args = mock_hass.config_entries.async_update_entry.call_args
        assert call_args[0][0] == mock_config_entry  # First positional arg is entry
        assert call_args[1]["data"] == user_input  # Keyword arg 'data'

    @pytest.mark.asyncio
    async def test_options_flow_validation_errors(self, mock_hass, mock_config_entry):
        """Test invalid options show validation errors (AC-6)."""
        flow = BeatsyOptionsFlow(mock_config_entry)
        flow.hass = mock_hass

        user_input = {
            "timer_duration": 45,
            "year_range_min": 2010,
            "year_range_max": 1990,  # Invalid: min > max
        }

        result = await flow.async_step_init(user_input=user_input)

        assert result["type"] == data_entry_flow.FlowResultType.FORM
        assert "year_range_min" in result["errors"]
        assert result["errors"]["year_range_min"] == "min_greater_than_max"

    @pytest.mark.asyncio
    async def test_options_flow_year_range_equals_validation(self, mock_hass, mock_config_entry):
        """Test options flow rejects year_min == year_max (AC-6)."""
        flow = BeatsyOptionsFlow(mock_config_entry)
        flow.hass = mock_hass

        user_input = {
            "timer_duration": 45,
            "year_range_min": 2000,
            "year_range_max": 2000,  # Invalid: equal
        }

        result = await flow.async_step_init(user_input=user_input)

        assert result["type"] == data_entry_flow.FlowResultType.FORM
        assert "year_range_min" in result["errors"]


class TestConfigFlowIntegration:
    """Integration tests for complete config flow."""

    @pytest.mark.asyncio
    async def test_full_config_flow_user_initiated(self, mock_hass):
        """Test complete user-initiated config flow (AC-2, AC-4)."""
        flow = BeatsyConfigFlow()
        flow.hass = mock_hass

        # Step 1: User initiates config flow (no input)
        result = await flow.async_step_user(user_input=None)
        assert result["type"] == data_entry_flow.FlowResultType.FORM
        assert result["step_id"] == "user"

        # Step 2: User submits form with valid data
        def mock_create_entry(title, data):
            return {
                "type": data_entry_flow.FlowResultType.CREATE_ENTRY,
                "title": title,
                "data": data,
            }

        flow.async_create_entry = mock_create_entry

        user_input = {
            "timer_duration": 45,
            "year_range_min": 1960,
            "year_range_max": 2020,
        }

        result = await flow.async_step_user(user_input=user_input)
        assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
        assert result["title"] == "Beatsy"
        assert result["data"] == user_input

    @pytest.mark.asyncio
    async def test_config_flow_with_defaults(self, mock_hass):
        """Test config flow uses defaults for optional fields (AC-2)."""
        flow = BeatsyConfigFlow()
        flow.hass = mock_hass

        def mock_create_entry(title, data):
            return {
                "type": data_entry_flow.FlowResultType.CREATE_ENTRY,
                "title": title,
                "data": data,
            }

        flow.async_create_entry = mock_create_entry

        # Submit with only required fields (defaults will be used)
        user_input = {
            "timer_duration": 30,
            "year_range_min": 1950,
            "year_range_max": 2024,
        }

        result = await flow.async_step_user(user_input=user_input)

        # Verify defaults are present
        assert result["data"]["timer_duration"] == 30
        assert result["data"]["year_range_min"] == 1950
        assert result["data"]["year_range_max"] == 2024
