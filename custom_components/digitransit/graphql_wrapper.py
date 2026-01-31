"""Wrap the GraphQL client to provide useful methods."""

from python_graphql_client import GraphqlClient
import requests

from .const import LOGGER


class DigitransitGraphQLError(Exception):
    """Non-specific error."""


class DigitransitNotAuthenticatedError(DigitransitGraphQLError):
    """Authentication failed."""


class DigitransitNoStopFoundError(DigitransitGraphQLError):
    """Zero matching stops returned."""


class DigitransitMultipleStopsFoundError(DigitransitGraphQLError):
    """Too many possible stops found."""


class DigitransitGraphQLWrapper:
    """An API client which wraps around a simple GraphQL client."""

    def __init__(self, api_key, data_region, route_lang, hass) -> None:
        """Create a new instance with an API key."""
        self.api_key = api_key
        self.hass = hass
        self.data_region = data_region

        route_lang = "*" if route_lang is None else route_lang
        headers = {"Accept-Language": route_lang}

        self.client = GraphqlClient(endpoint=self.endpoint(), headers=headers)

    def endpoint(self) -> str:
        """Get the right endpoint for the selected region, with the API key ready-appended."""
        match self.data_region:
            case "hsl":
                return f"https://api.digitransit.fi/routing/v2/hsl/gtfs/v1?digitransit-subscription-key={self.api_key}"
            case "waltti":
                return f"https://api.digitransit.fi/routing/v2/waltti/gtfs/v1?digitransit-subscription-key={self.api_key}"
            case "digitransit":
                return f"https://api.digitransit.fi/routing/v2/finland/gtfs/v1?digitransit-subscription-key={self.api_key}"
        raise Exception("Invalid data_region")

    def sync_all_feeds(self):
        """Get a list of regions and the name of the respectie publisher."""
        query = "{feeds{feedId,publisher{name}}}"
        try:
            results = self.client.execute(query=query)
        except requests.exceptions.HTTPError as exception:
            LOGGER.warn(exception)
            raise DigitransitNotAuthenticatedError("API key rejected")
        else:
            return {
                feed["feedId"]: feed["publisher"]["name"]
                for feed in results["data"]["feeds"]
            }

    async def all_feeds(self):
        """Call sync_all_feeds async."""
        return await self.hass.async_add_executor_job(self.sync_all_feeds)

    def sync_get_stop_name_and_id_by_code(self, stop_code):
        """Find a stop name and ID from a stop code or name."""
        query = """query stopQuery($stop_code: String) { stops(name: $stop_code){name,desc,code,platformCode,gtfsId}}"""
        variables = {"stop_code": stop_code}
        LOGGER.debug(query)
        results = self.client.execute(query=query, variables=variables)
        LOGGER.debug(results)
        if len(results["data"]["stops"]) == 0:
            # No results
            raise DigitransitNoStopFoundError
        elif len(results["data"]["stops"]) > 1:
            # Too many results
            raise DigitransitMultipleStopsFoundError
        else:
            # Good to go
            stop = results["data"]["stops"][0]
            return stop["name"] + " (" + stop["code"] + ")", stop["gtfsId"]

    async def get_stop_name_and_id_by_code(self, stop_code):
        """Call sync_get_stop_name_and_id async."""
        return await self.hass.async_add_executor_job(
            self.sync_get_stop_name_and_id_by_code, stop_code
        )

    def sync_get_stop_name_and_id_by_gtfs(self, gtfs_id):
        """Find a stop name and ID from a GTFS id."""
        query = f"""{{ stop(id: "{gtfs_id}"){{name,code,platformCode,gtfsId}}}}"""
        LOGGER.debug(query)
        results = self.client.execute(query=query)
        LOGGER.debug(results)
        if len(results["data"]["stop"]) == {}:
            # No results
            raise DigitransitNoStopFoundError
        else:
            # Good to go
            stop = results["data"]["stop"]
            output = [stop["name"]]
            if stop["code"]:
                output.append("(" + stop["code"] + ")")
            return " ".join(output), stop["gtfsId"]

    async def get_stop_name_and_id_by_gtfs(self, gtfs_id):
        """Call sync_get_stop_name_and_id async."""
        return await self.hass.async_add_executor_job(
            self.sync_get_stop_name_and_id_by_gtfs, gtfs_id
        )

    def sync_get_stop_data(self, gtfs_id, number_of_departures):
        """Get stop times from a saved GTFS id."""
        try:
            query = """{ stop(id: "$stop_id") { name, vehicleMode, stoptimesWithoutPatterns(numberOfDepartures: $number_of_departures) { scheduledDeparture, realtimeDeparture, departureDelay, realtime, realtimeState, serviceDay, headsign, trip { routeShortName } } } }"""
            results = self.client.execute(
                query=query.replace("$stop_id", gtfs_id).replace(
                    "$number_of_departures", str(number_of_departures)
                )
            )
            LOGGER.debug(results)
            return results
        except requests.exceptions.HTTPError as exception:
            if exception.args[0].startswith("401"):
                raise DigitransitNotAuthenticatedError("API key rejected")
            else:
                raise exception

    async def get_stop_data(self, gtfs_id, number_of_departures):
        """Call sync_get_stop_data async."""
        return await self.hass.async_add_executor_job(
            self.sync_get_stop_data, gtfs_id, number_of_departures
        )
