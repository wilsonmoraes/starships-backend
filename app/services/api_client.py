import os

from dotenv import load_dotenv

load_dotenv()
BASE_URL = os.environ["BASE_URL"]

from typing import Any, Dict

import requests


class SWAPIClient:

    @staticmethod
    def get_starships(page: int = 1, limit=10, name: str = "", model: str = ""):

        url = f"{BASE_URL}/starships/?page={page}&limit={limit}"
        if name:
            url += f"&name={name}"
        if model:
            url += f"&model={model}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def get_starship_by_id(starship_id: str) -> Dict[str, Any]:
        """
        Fetch a single starship by ID from the SWAPI.
        """
        url = f"{BASE_URL}/starships/{starship_id}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
