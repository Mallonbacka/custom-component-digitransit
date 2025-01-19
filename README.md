This is a custom component for Home Assistant, which adds a single stop (bus
or tram stop, train or metro platform) from Helsinki Region Transport
(Helsingin seudun liikenne, HSL, Helsingforsregionens trafik, HRT),
Waltti or another Digitransit-supported region as a Home Assistant sensor.

Search for a stop using the name or stop code. Search results will include extra
details, like the stop code or platform number, which should allow you to tell
them apart if there are several results.

You'll also need a Digitransit API key. You can sign up for one for free
on [the Digitransit website](https://digitransit.fi/en/developers/api-registration/).

## Pre-release warning

The basic functionality works, but this isn't yet ready for wider use, so
use this at your own risk.

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
