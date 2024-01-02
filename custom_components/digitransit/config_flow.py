"""Adds config flow for Digitransit."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import DOMAIN

from .graphql_wrapper import (
    DigitransitGraphQLWrapper,
    DigitransitNotAuthenticatedError,
    DigitransitMultipleStopsFoundError,
    DigitransitNoStopFoundError
)

class DigitransitFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Blueprint."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.FlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            try:
                await self._test_api_key(
                    digitransit_api_key=user_input["digitransit_api_key"],
                )
            except DigitransitNotAuthenticatedError:
                _errors["base"] = "auth"
            else:
                try:
                    stop_name, api_id = await self._get_stop_name_and_id(user_input['stop_code'])
                except DigitransitNoStopFoundError:
                    _errors["base"] = "no_stop_found"
                except DigitransitMultipleStopsFoundError:
                    _errors["base"] = "too_many_stops"
                else:
                    return self.async_create_entry(
                        title=stop_name,
                        data=user_input | { "gtfs_id": api_id },
                    )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("digitransit_api_key", default=(user_input or {}).get("digitransit_api_key")) : selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT
                        ),
                    ),
                    vol.Required("stop_code", default=(user_input or {}).get("stop_code")) : selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT
                        )
                    )
                }
            ),
            errors=_errors,
        )

    async def _test_api_key(self, digitransit_api_key: str) -> None:
        """Validate credentials."""
        self.client = DigitransitGraphQLWrapper(digitransit_api_key, hass=self.hass)
        await self.client.test_api_key()

    async def _get_stop_name_and_id(self, stop_code: str) -> str:
        """Get the official stop name for the code."""
        return await self.client.get_stop_name_and_id(stop_code)
