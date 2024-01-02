"""DataUpdateCoordinator for digitransit."""
from __future__ import annotations

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
)

from .graphql_wrapper import (
    DigitransitGraphQLWrapper
)
from .const import DOMAIN, LOGGER

class DigitransitDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage updating the entities."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        client: DigitransitGraphQLWrapper,
    ) -> None:
        """Initialize the coordinator."""
        self.client = client
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=1),
        )

    async def _async_update_data(self):
        """Update data from endpoint."""
        return await self.client.get_stop_data(self.config_entry.data['gtfs_id'])
