"""Transform data for display."""

from datetime import datetime
import math

from .const import COMPACT_DEPARTURES_CHARS, SHORT_HEADSIGN_CHARS


def format_departure_row(row, timezone):
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
    row["shortHeadsign"] = short_headsign(row["headsign"])
    row.pop("serviceDay")
    return row


def departureToNumberOfMinutes(row):
    """Convert a departure into a number of minutes."""
    departsAt = datetime.fromtimestamp(row["serviceDay"] + row["realtimeDeparture"])
    delta = departsAt - datetime.now()
    return math.floor(delta.total_seconds() / 60)


def list_to_compact_departures(departures):
    """Convert the departures list to a string."""
    if len(departures) == 0:
        return ""
    res = departure_to_string(departures[0])

    prev_hour = departures[0]["realtimeDeparture"].hour
    sep = ", "
    for departure in departures[1 : len(departures) - 1]:
        curr_hour = departure["realtimeDeparture"].hour
        skip_hour = curr_hour == prev_hour
        next_route = departure_to_string(departure, skip_hour)
        if len(res) + len(sep) + len(next_route) <= COMPACT_DEPARTURES_CHARS:
            res += sep + next_route
        else:
            break
        prev_hour = curr_hour

    return res


def departure_to_string(departure, hide_hours=False):
    """Convert a single departure to a string of route number + departure time."""
    tm_str = ""
    if not hide_hours:
        tm_str = f"{departure['realtimeDeparture'].hour:02d}"
    tm_str = tm_str + ":" + f"{departure['realtimeDeparture'].minute:02d}"
    return f"{tm_str} {departure['route']}"


def short_headsign(full_headsign):
    """To fit into small spaces, we limit the length of this."""
    if len(full_headsign) > SHORT_HEADSIGN_CHARS:
        if " " in full_headsign:
            full_headsign = full_headsign.split(" ")[0]
    return full_headsign
