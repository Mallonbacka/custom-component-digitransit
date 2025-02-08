"""Adds config flow for Digitransit."""

from __future__ import annotations
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import DOMAIN
from .geocoding_client import GeocodingClient

from .graphql_wrapper import (
    DigitransitGraphQLWrapper,
    DigitransitNotAuthenticatedError,
)


class DigitransitFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Digitransit instance."""

    VERSION = 2

    data: dict[str, Any] | None

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.FlowResult:
        """Step 1 - Handle a flow initialized by the user, collect API key."""
        _errors = {}
        if user_input is not None:
            try:
                all_feeds = await self.all_feeds(
                    user_input["digitransit_api_key"], user_input["data_region"]
                )
            except DigitransitNotAuthenticatedError:
                _errors["base"] = "auth"
            else:
                self.data = {
                    "digitransit_api_key": user_input["digitransit_api_key"],
                    "data_region": user_input["data_region"],
                    "all_feeds": all_feeds,
                }
                return await self.async_step_stop_info()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        "digitransit_api_key",
                        default=(user_input or {}).get("digitransit_api_key", ""),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT
                        ),
                    ),
                    vol.Required(
                        "data_region",
                        default=(user_input or {}).get("data_region", None),
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=["hsl", "waltti", "digitransit"],
                            translation_key="data_regions",
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
        """Step 2 - once API key is confirmed working, run the search."""
        _errors = {}
        if user_input is not None:
            assert self.data
            search_results = await self.identify_stop(
                user_input["search_term"],
                self.data_region,
                user_input.get("feed_id") or list(self.data["all_feeds"].keys())[0],
            )
            if len(search_results) == 0:
                _errors["base"] = "no_stop_found"
            else:
                self.data = (
                    (self.data or {}) | user_input | {"search_results": search_results}
                )
                return await self.async_step_select_stop(None)

        assert self.data

        select_options = [
            selector.SelectOptionDict(label=label, value=feed_id)
            for feed_id, label in self.data["all_feeds"].items()
        ]
        fields = {}
        if len(select_options) != 1:
            fields[
                vol.Required(
                    "feed_id",
                    default=(user_input or {}).get("feed_id", None),
                )
            ] = selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=select_options,
                ),
            )
        fields[
            vol.Required(
                "search_term", default=(user_input or {}).get("search_term", "")
            )
        ] = selector.TextSelector(
            selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
        )
        return self.async_show_form(
            step_id="stop_info",
            data_schema=vol.Schema(fields),
            errors=_errors,
        )

    async def async_step_select_stop(
        self,
        user_input: dict | None = None,
    ):
        """Step 3 - render the search results as a selectable list."""
        if user_input is not None:
            stop_name, gtfs_id = await self._get_stop_name_and_id_by_gtfs(
                user_input["stop_gtfs_id"]
            )
            return self.async_create_entry(
                title=stop_name,
                data=(self.data or {}) | user_input | {"gtfs_id": gtfs_id},
            )
        else:
            # Show the list
            assert self.data
            select_options = [
                selector.SelectOptionDict(label=label, value=gtfs_id)
                for gtfs_id, label in self.data["search_results"].items()
            ]
            return self.async_show_form(
                step_id="select_stop",
                data_schema=vol.Schema(
                    {
                        vol.Required(
                            "stop_gtfs_id",
                            default=(user_input or {}).get("stop_gtfs_id", None),
                        ): selector.SelectSelector(
                            selector.SelectSelectorConfig(
                                options=select_options,
                            ),
                        )
                    }
                ),
            )

    async def identify_stop(self, search_term, data_region, feed_id):
        """Take the search criteria and return a stop name and code."""
        self.data_region = data_region
        self.feed_id = feed_id
        return await self._search_for_stop(search_term)

    async def all_feeds(self, digitransit_api_key: str, data_region: str) -> dict:
        """Get all regions."""
        self.api_key = digitransit_api_key
        self.data_region = data_region
        self.client = DigitransitGraphQLWrapper(
            self.api_key, self.data_region, hass=self.hass
        )
        return await self.client.all_feeds()

    async def _search_for_stop(self, search_term: str) -> dict:
        assert self.data
        assert self.data["digitransit_api_key"]
        client = GeocodingClient(self.data["digitransit_api_key"])
        return await self.hass.async_add_executor_job(
            client.search, self.feed_id, search_term
        )

    async def _get_stop_name_and_id_by_gtfs(self, gtfs_id: str) -> str:
        """Get the official stop name for the code."""
        client = DigitransitGraphQLWrapper(
            self.api_key, self.data_region, hass=self.hass
        )
        return await client.get_stop_name_and_id_by_gtfs(gtfs_id)
