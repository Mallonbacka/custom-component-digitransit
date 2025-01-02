"""Transform data for display."""
from datetime import datetime, timedelta
import math

def formatDepartureRow(row, timezone):
    """Simplify the departure information for use in the attribute."""
    row['scheduledDeparture'] = datetime.fromtimestamp(row['serviceDay'], timezone) + timedelta(seconds=row['scheduledDeparture'])
    row['realtimeDeparture'] = datetime.fromtimestamp(row['serviceDay'], timezone) + timedelta(seconds=row['realtimeDeparture'])
    row['route'] = row.pop('trip')['routeShortName']
    row.pop('serviceDay')
    return row

def departureToNumberOfMinutes(row):
    """Convert a departure into a number of minutes."""
    departsAt = datetime.fromtimestamp(row['serviceDay'] + row['realtimeDeparture'])
    delta = departsAt - datetime.now()
    return math.floor(delta.total_seconds() / 60)

