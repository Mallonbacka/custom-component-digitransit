"""DigitransitEntity class."""

from __future__ import annotations

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION
from .coordinator import DigitransitDataUpdateCoordinator


class DigitransitEntity(CoordinatorEntity):
    """A single configured instance of the component."""

    _attr_attribution = ATTRIBUTION

    def __init__(self, coordinator: DigitransitDataUpdateCoordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_unique_id = coordinator.config_entry.entry_id
