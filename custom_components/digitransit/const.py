"""Constants for Digitransit."""

from datetime import timedelta

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

NAME = "Digitransit"
DOMAIN = "digitransit"
VERSION = "0.0.0"
ATTRIBUTION = "Data from Digitransit"

INTERVAL = timedelta(seconds=60)
COMPACT_DEPARTURES_CHARS = 28
SHORT_HEADSIGN_CHARS = 15
