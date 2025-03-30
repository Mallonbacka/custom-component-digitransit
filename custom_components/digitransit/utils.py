"""Transform data for display."""

from datetime import datetime
import math


def formatDepartureRow(row, timezone):
    """Simplify the departure information for use in the attribute."""
    scheduledDepartureTimestamp = row["serviceDay"] + row["scheduledDeparture"]
    row["scheduledDeparture"] = datetime.fromtimestamp(
        scheduledDepartureTimestamp, timezone
    )
    realtimeDepartureTimestamp = row["serviceDay"] + row["realtimeDeparture"]
    row["realtimeDeparture"] = datetime.fromtimestamp(
        realtimeDepartureTimestamp, timezone
    )
    row["route"] = row.pop("trip")["routeShortName"]
    row.pop("serviceDay")
    return row


def departureToNumberOfMinutes(row):
    """Convert a departure into a number of minutes."""
    departsAt = datetime.fromtimestamp(row["serviceDay"] + row["realtimeDeparture"])
    delta = departsAt - datetime.now()
    return math.floor(delta.total_seconds() / 60)
