"""Adds config flow for Digitransit."""
from __future__ import annotations
from typing import Any

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

    VERSION = 2

    data: dict[str, Any] | None

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
                self.data = {
                    "digitransit_api_key": user_input["digitransit_api_key"]}
                return await self.async_step_stop_info()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("digitransit_api_key", default=(user_input or {}).get("digitransit_api_key")): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT
                        ),
                    ),
                }
            ),
            errors=_errors,
        )

    async def async_step_stop_info(
        self,
        user_input: dict | None = None,
    ) -> config_entries.FlowResult:
        """Step 2 - once API key is confirmed working."""
        _errors = {}
        if user_input is not None:
            try:
                stop_name, api_id = await self.identify_stop(user_input['search_type'], user_input['search_term'])
            except DigitransitNoStopFoundError:
                _errors["base"] = "no_stop_found"
            except DigitransitMultipleStopsFoundError:
                _errors["base"] = "too_many_stops"
            else:
                return self.async_create_entry(
                    title=stop_name,
                    data=self.data | user_input | {"gtfs_id": api_id},
                )

        return self.async_show_form(
            step_id="stop_info",
            data_schema=vol.Schema(
                {
                    vol.Required("data_region", default=(user_input or {}).get("data_region")): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=["hsl", "waltti", "digitransit"],
                            translation_key="data_regions",
                        ),
                    ),
                    vol.Required("search_type", default=(user_input or {}).get("search_type")): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=["stop_code", "stop_gtfs_id"],
                            translation_key="search_types",
                        ),
                    ),
                    vol.Required("search_term", default=(user_input or {}).get("search_term")): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT
                        )
                    )
                }
            ),
            errors=_errors,
        )

    async def identify_stop(self, search_type, search_term):
        """Take the search criteria and return a stop name and code."""
        if (search_type == "stop_code"):
            return await self._get_stop_name_and_id_by_code(search_term)
        elif (search_type == "stop_gtfs_id"):
            return await self._get_stop_name_and_id_by_gtfs(search_term)
        else:
            raise DigitransitNoStopFoundError

    async def _test_api_key(self, digitransit_api_key: str) -> None:
        """Validate credentials."""
        self.client = DigitransitGraphQLWrapper(
            digitransit_api_key, "hsl", hass=self.hass)
        await self.client.test_api_key()

    async def _get_stop_name_and_id_by_code(self, stop_code: str) -> str:
        """Get the official stop name for the code."""
        return await self.client.get_stop_name_and_id_by_code(stop_code)

    async def _get_stop_name_and_id_by_gtfs(self, gtfs_id: str) -> str:
        """Get the official stop name for the code."""
        return await self.client.get_stop_name_and_id_by_gtfs(gtfs_id)
