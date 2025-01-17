from functools import lru_cache

import requests

BASE_URL = "https://swapi.tech/api/starships"


@lru_cache(maxsize=32)
def fetch_starships():
    response = requests.get(BASE_URL).json()
    total_pages = response["total_pages"]

    starships = []
    for page in range(1, total_pages + 1):
        page_url = f"{BASE_URL}?page={page}"
        page_response = requests.get(page_url).json()
        starships += page_response["results"]

    return starships


@lru_cache(maxsize=128)
def fetch_starship_details(uid):
    url = f"https://swapi.tech/api/starships/{uid}/"
    response = requests.get(url).json()
    return response["result"]["properties"]


def get_detailed_starships():
    starships = fetch_starships()
    detailed_starships = []
    for ship in starships:
        details = fetch_starship_details(ship["url"])
        detailed_starships.append({"name": details["name"], "manufacturer": details["manufacturer"]})
    return detailed_starships
