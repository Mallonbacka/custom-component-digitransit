"""Sensor platform for digitransit."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.const import UnitOfTime

from .const import DOMAIN
from .coordinator import DigitransitDataUpdateCoordinator
from .entity import DigitransitEntity
from .utils import formatDepartureRow, departureToNumberOfMinutes

ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key="digitransit",
    ),
)


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        DigitransitSensor(
            coordinator=coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class DigitransitSensor(DigitransitEntity, SensorEntity):
    """digitransit Sensor class."""

    _unrecorded_attributes = frozenset({"departures"})

    def __init__(
        self,
        coordinator: DigitransitDataUpdateCoordinator,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self.entity_description = entity_description

    @property
    def native_value(self) -> str:
        """Return the native value of the sensor."""
        departures = (
            self.coordinator.data.get("data")
            .get("stop")
            .get("stoptimesWithoutPatterns")
        )
        if len(departures) > 0:
            return departureToNumberOfMinutes(departures[0])
        else:
            return None

    @property
    def native_unit_of_measurement(self):
        """Sensor displays minutes until next departure."""
        return UnitOfTime.MINUTES

    @property
    def extra_state_attributes(self):
        """Attributes contain a list of the next few departures."""
        departure_list = (
            self.coordinator.data.get("data")
            .get("stop")
            .get("stoptimesWithoutPatterns")
        )
        departure_list = list(map(formatDepartureRow, departure_list))
        return {"departures": departure_list}

    @property
    def icon(self):
        """Icon reflects the transport mode, but falls back to a bus."""
        vehicle_mode = self.coordinator.data.get("data").get("stop").get("vehicleMode")
        match vehicle_mode.lower():
            case "bus":
                return "mdi:bus"
            case "ferry":
                return "mdi:ferry"
            case "rail":
                return "mdi:train-variant"
            case "subway":
                return "mdi:subway"
            case "tram":
                return "mdi:tram"
            case _:
                return "mdi:bus"

    @property
    def name(self):
        """Entity title is the official stop name."""
        return self.coordinator.config_entry.title + " next departure"
