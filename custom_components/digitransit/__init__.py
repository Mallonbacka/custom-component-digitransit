"""Custom integration to integrate digitransit with Home Assistant.

For more details about this integration, please refer to
https://github.com/ludeeus/digitransit
"""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .graphql_wrapper import DigitransitGraphQLWrapper
from .const import DOMAIN, LOGGER
from .coordinator import DigitransitDataUpdateCoordinator

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
]


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up this integration using UI."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator = DigitransitDataUpdateCoordinator(
        hass=hass,
        client=DigitransitGraphQLWrapper(
            entry.data['digitransit_api_key'], entry.data['data_region'], hass),
    )
    # https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    if unloaded := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


async def async_migrate_entry(hass, entry):
    """Migrate config to latest version."""
    LOGGER.debug("Migrating configuration from version %s",
                 entry.version)

    if entry.version > 1:
        return False

    if entry.version == 1:
        new_data = {**entry.data}
        new_data['data_region'] = entry.data.get('data_region', "hsl")
        pass

    hass.config_entries.async_update_entry(
        entry, data=new_data, version=2)

    LOGGER.debug(
        "Migration to configuration version %s successful", entry.version)

    return True
