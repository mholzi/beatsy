"""Config flow for Beatsy integration.

Provides UI-based setup following Home Assistant 2025 best practices.
Users can configure:
- Timer duration (10-120 seconds)
- Year range for song guessing (1900-2024)

Supports reconfiguration via HA options flow.
"""
from __future__ import annotations

from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN

# Configuration schema for initial setup
CONFIG_SCHEMA = vol.Schema(
    {
        vol.Optional("timer_duration", default=30): vol.All(
            cv.positive_int,
            vol.Range(min=10, max=120)
        ),
        vol.Optional("year_range_min", default=1950): vol.All(
            cv.positive_int,
            vol.Range(min=1900, max=2024)
        ),
        vol.Optional("year_range_max", default=2024): vol.All(
            cv.positive_int,
            vol.Range(min=1900, max=2024)
        ),
    }
)


class BeatsyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Beatsy."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial configuration step.

        Args:
            user_input: User input from the config flow form (None for initial display).

        Returns:
            FlowResult with either form display or entry creation.
        """
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate year range consistency
            year_min = user_input.get("year_range_min", 1950)
            year_max = user_input.get("year_range_max", 2024)

            if year_min >= year_max:
                errors["year_range_min"] = "min_greater_than_max"

            if not errors:
                # Create config entry with user data
                return self.async_create_entry(
                    title="Beatsy",
                    data=user_input,
                )

        # Show configuration form
        return self.async_show_form(
            step_id="user",
            data_schema=CONFIG_SCHEMA,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> BeatsyOptionsFlow:
        """Get the options flow for this handler.

        Args:
            config_entry: The config entry to create options flow for.

        Returns:
            BeatsyOptionsFlow instance.
        """
        return BeatsyOptionsFlow(config_entry)


class BeatsyOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Beatsy."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow.

        Args:
            config_entry: The config entry being configured.
        """
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options.

        Args:
            user_input: User input from options form (None for initial display).

        Returns:
            FlowResult with either form display or entry update.
        """
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate year range consistency
            year_min = user_input.get("year_range_min", 1950)
            year_max = user_input.get("year_range_max", 2024)

            if year_min >= year_max:
                errors["year_range_min"] = "min_greater_than_max"

            if not errors:
                # Update config entry data (not options, to maintain consistency)
                self.hass.config_entries.async_update_entry(
                    self.config_entry,
                    data=user_input
                )
                # Return create_entry to complete the flow
                return self.async_create_entry(title="", data={})

        # Pre-fill with current values from entry data
        current_config = self.config_entry.data
        schema = vol.Schema(
            {
                vol.Optional(
                    "timer_duration",
                    default=current_config.get("timer_duration", 30)
                ): vol.All(cv.positive_int, vol.Range(min=10, max=120)),
                vol.Optional(
                    "year_range_min",
                    default=current_config.get("year_range_min", 1950)
                ): vol.All(cv.positive_int, vol.Range(min=1900, max=2024)),
                vol.Optional(
                    "year_range_max",
                    default=current_config.get("year_range_max", 2024)
                ): vol.All(cv.positive_int, vol.Range(min=1900, max=2024)),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            errors=errors,
        )
