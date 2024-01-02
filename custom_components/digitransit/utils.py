"""Transform data for display."""
from datetime import datetime
import math

def formatDepartureRow(row):
    """Simplify the departure information for use in the attribute."""
    row['scheduledDeparture'] = datetime.fromtimestamp(row['serviceDay'] + row['scheduledDeparture'])
    row['realtimeDeparture'] = datetime.fromtimestamp(row['serviceDay'] + row['realtimeDeparture'])
    row['route'] = row.pop('trip')['routeShortName']
    row.pop('serviceDay')
    return row

def departureToNumberOfMinutes(row):
    """Convert a departure into a number of minutes."""
    departsAt = datetime.fromtimestamp(row['serviceDay'] + row['realtimeDeparture'])
    delta = departsAt - datetime.now()
    return math.floor(delta.total_seconds() / 60)

