import os
from typing import Tuple, Optional

import requests
from dotenv import load_dotenv

load_dotenv()

HERE_API_KEY = os.getenv("HERE_API_KEY")


def geocode_location(location: str) -> Optional[Tuple[float, float]]:
    """
    Convert a location name to latitude and longitude using HERE Maps API.
    """
    base_url = "https://geocode.search.hereapi.com/v1/autosuggest"
    params = {
        "q": location,
        "in": "circle:12.9716,77.5946;r=100000",  # Center of Bangalore with 100km radius
        "apiKey": HERE_API_KEY,
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        results = response.json()

        # Find the first result of type "locality"
        locality_result = next(
            (
                item
                for item in results.get("items", [])
                if item.get("resultType") == "locality"
            ),
            None,
        )

        if locality_result:
            position = locality_result.get("position")
            if position:
                return float(position["lat"]), float(position["lng"])
    except Exception as e:
        print(f"Error parsing geocoding response: {e}")

    return None
