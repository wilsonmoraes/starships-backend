from typing import List

from app.models.schemas.starships import Starship
from app.services.api_client import SWAPIClient


class StarshipService:
    @staticmethod
    def fetch_all_starships(page: int = 1, name: str = None, model: str = None) -> List[Starship]:
        """
        Fetch all starships and return them as a list of Starship models.
        """
        data = SWAPIClient.get_starships(page=page, name=name, model=model)
        starships = data.get("results", [])
        return [Starship(**starship["properties"]) for starship in starships]

    @staticmethod
    def fetch_starship_by_id(starship_id: int) -> Starship:
        """
        Fetch a single starship by ID and return it as a Starship model.
        """
        data = SWAPIClient.get_starship_by_id(starship_id)
        return Starship(**data["result"]["properties"])
