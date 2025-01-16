from pydantic import BaseModel
from typing import List, Optional

class Starship(BaseModel):
    name: str
    model: str
    starship_class: str
    manufacturer: str
    cost_in_credits: Optional[str]
    length: Optional[str]
    crew: Optional[str]
    passengers: Optional[str]
    max_atmosphering_speed: Optional[str]
    hyperdrive_rating: Optional[str]
    MGLT: Optional[str]
    cargo_capacity: Optional[str]
    consumables: Optional[str]
    films: List[str]
    pilots: List[str]
    url: str
