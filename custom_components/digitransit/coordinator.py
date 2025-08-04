"""DataUpdateCoordinator for digitransit."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
)
from homeassistant.helpers import issue_registry as ir

from .graphql_wrapper import DigitransitGraphQLWrapper, DigitransitNotAuthenticatedError
from .const import DOMAIN, LOGGER


class DigitransitDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage updating the entities."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        client: DigitransitGraphQLWrapper,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the coordinator."""
        self.client = client
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=1),
            config_entry=config_entry,
        )

    async def _async_update_data(self):
        """Update data from endpoint."""
        try:
            return await self.client.get_stop_data(self.config_entry.data["gtfs_id"])
        except DigitransitNotAuthenticatedError:
            ir.async_create_issue(
                self.hass,
                DOMAIN,
                "api_key_rejected",
                is_fixable=True,
                severity=ir.IssueSeverity.ERROR,
                translation_key="api_key_rejected",
                data={"entry_id": self.config_entry.entry_id},
            )
            await self.config_entry.async_unload(self.hass)
