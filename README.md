This is a custom component for Home Assistant, which adds a single stop (bus
or tram stop, train or metro platform) from Helsinki Region Transport
(Helsingin seudun liikenne, HSL) as a Home Assistant sensor.

You can add a stop using either:

- The stop number, which you can find on a sign at the
stop or from the journey planner (reittiopas). For example, for trams from
Länsiterminaali T1 going towards central Helsinki, you'd use H0236. For
platform 1 at Tapiola bus station, you'd use E2187.
- The GTFS identifier of the stop. This is useful if two stops
share a single stop number. You can find this URL encoded inside the address
of the journey planner page for the stop. For example, Alberganesplanadi
([E1112](https://reittiopas.hsl.fi/pysakit/HSL%3A2112231?locale=en))
has the address `pysakit/HSL%3A2112231`, and the GTFS identifier `HSL:2112231` -
swap the `%3A` for a colon.

You'll also need a Digitransit API key. You can sign up for one for free
on [the Digitransit website](https://digitransit.fi/en/developers/api-registration/).

## Pre-release warning

The basic functionality works, but this isn't yet ready for wider use, so
use this at your own risk. One key limitation at present is that some
HSL-specific arguments are hard-coded, whereas the API supports all
Digitransit-supported areas of Finland.

Another limitation is that stations are not currently supported, only
stops. This means you can't monitor all departures from a station
with multiple stops or platforms.

Before a stable release, these will be addressed, and it's possible that
addressing these will break the current functionality, so if you want to
use this already, please check the release notes carefully before upgrading.

## Installation

Installing with HACS is recommended.

First, install the custom integration using [HACS](https://hacs.xyz/):

1. Add the integration using HACS
1. Restart Home Assistant

[![Open your Home Assistant instance and open the CloudWatch custom component repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Mallonbacka&repository=custom-component-digitransit)

Then add a new integraion:

1. Go to **Settings**, then **Devices & Services**
1. Click **Add Integration**
1. Select 'Digitransit' from the list
1. Enter your API key and stop number.

## Usage

The sensor counts down to the next uncancelled departure. The attributes
provide a list of upcoming departures with their service name and departure
time in a machine-friendly format.

## Credits

This repository is based on the excellent [integration_blueprint](https://github.com/ludeeus/integration_blueprint)
template.
