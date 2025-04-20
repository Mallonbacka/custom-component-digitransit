"""Class to wrap calls to the Geocoding API for stop search during config."""

import requests

SEARCH_ENDPOINT = "https://api.digitransit.fi/geocoding/v1/search"


class GeocodingClient:
    """REST client for Digitransit Geocoding API."""

    def __init__(self, api_key, search_lang):
        """Initialize a new client with an API key."""
        self.api_key = api_key
        self.search_lang = search_lang

    def search(self, feed, search_string):
        """Search for the given string in the given feed."""
        params = {
            "layers": "stop",
            "size": 5,
            "text": search_string,
            "sources": "gtfs" + feed,
            "digitransit-subscription-key": self.api_key,
        }
        if self.search_lang is not None:
            params["lang"] = self.search_lang

        response = requests.get(SEARCH_ENDPOINT, params)
        return {
            self.trim_gtfs_id(feat["properties"]["id"]): self.format_label(
                feat["properties"]
            )
            for feat in response.json()["features"]
        }

    def trim_gtfs_id(self, full_id):
        """Remove the prefix and suffix from the GTFS ID."""
        return full_id.replace("GTFS:", "").split("#")[0]

    def format_label(self, properties):
        """Add platform information or GTFS ID to label."""
        label = properties["label"]
        if properties["addendum"]:
            if properties["addendum"].get("GTFS"):
                if properties["addendum"]["GTFS"].get("platform"):
                    label = (
                        label
                        + ", platform "
                        + properties["addendum"]["GTFS"]["platform"]
                    )
                if properties["addendum"]["GTFS"].get("code"):
                    if properties["addendum"]["GTFS"]["code"] not in label:
                        label = (
                            label + " (" + properties["addendum"]["GTFS"]["code"] + ")"
                        )
        else:
            label = label + "(GTFS: " + self.trim_gtfs_id(properties["id"]) + ")"
        return label
