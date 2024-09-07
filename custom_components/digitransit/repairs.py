"""Repair for non-working Digitransit API key."""

from __future__ import annotations
from typing import Any

import voluptuous as vol
from homeassistant.helpers import selector

from homeassistant import data_entry_flow
from homeassistant.components.repairs import RepairsFlow
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .graphql_wrapper import (
    DigitransitGraphQLWrapper,
    DigitransitNotAuthenticatedError,
)


class ReplaceAPIKeyFlow(RepairsFlow):
    """Handler for an issue fixing flow."""

    data: dict[str, Any] | None

    def __init__(self, entry: ConfigEntry) -> None:
        """Create flow."""
        self.entry = entry

    async def async_step_init(
        self, user_input: dict[str, str]
    ) -> data_entry_flow.FlowResult:
        """Handle the first step of the API key replacement flow."""
        _errors = {}
        if user_input.get("digitransit_api_key") is not None:
            try:
                await self._test_api_key(
                    digitransit_api_key=user_input.get("digitransit_api_key", ""),
                )
            except DigitransitNotAuthenticatedError:
                _errors["base"] = "auth"
            else:
                self.data = self.entry.data | {
                    "digitransit_api_key": user_input["digitransit_api_key"]
                }
                # New key works - replace it
                self.hass.config_entries.async_update_entry(self.entry, data=self.data)
                await self.hass.config_entries.async_reload(self.entry.entry_id)

                return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        "digitransit_api_key",
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT
                        ),
                    ),
                }
            ),
            errors=_errors,
        )

    async def _test_api_key(self, digitransit_api_key: str) -> None:
        """Validate credentials."""
        # TODO: DRY
        self.api_key = digitransit_api_key
        # Single-use client, as the user hasn't chosen a region yet
        client = DigitransitGraphQLWrapper(self.api_key, "hsl", hass=self.hass)
        await client.test_api_key()


async def async_create_fix_flow(
    hass: HomeAssistant,
    issue_id: str,
    data: dict[str, str],
) -> RepairsFlow:
    """Create flow."""
    if issue_id == "api_key_rejected":
        entry = hass.config_entries.async_get_entry(data["entry_id"])
        assert entry
        return ReplaceAPIKeyFlow(entry)
