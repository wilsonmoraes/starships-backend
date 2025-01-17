import os
from unittest.mock import patch

from app.services.api_client import SWAPIClient  # Ajuste o caminho se necessário

os.environ["BASE_URL"] = "https://swapi.dev/api"


@patch("app.services.api_client.requests.get")
def test_get_starships(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "count": 1,
        "results": [{"name": "Millennium Falcon", "model": "YT-1300"}]
    }

    result = SWAPIClient.get_starships(page=1, limit=1, name="Falcon", model="YT-1300")

    mock_get.assert_called_with(
        "https://www.swapi.tech/api/starships/?page=1&limit=1&name=Falcon&model=YT-1300"
    )

    assert result["count"] == 1
    assert result["results"][0]["name"] == "Millennium Falcon"
