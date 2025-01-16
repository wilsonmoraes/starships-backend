from typing import Dict, Any

import requests


class SWAPIClient:
    BASE_URL = "https://www.swapi.tech/api"

    @staticmethod
    def get_starships(page: int = 1, name: str = None, model: str = None):
        """
        Fetch all starships from the SWAPI with optional search by name or model.
        Args:
            page (int): Page number for pagination.
            name (str, optional): Filter by starship name.
            model (str, optional): Filter by starship model.

        """
        url = f"{SWAPIClient.BASE_URL}/starships/?page={page}"
        if name:
            url += f"&name={name}"
        if model:
            url += f"&model={model}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def get_starship_by_id(starship_id: int) -> Dict[str, Any]:
        """
        Fetch a single starship by ID from the SWAPI.
        """
        url = f"{SWAPIClient.BASE_URL}/starships/{starship_id}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
