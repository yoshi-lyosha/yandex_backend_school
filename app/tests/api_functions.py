import requests

from app.tests.utils import get_server_api


def import_citizens(import_data: dict) -> int:
    server_api = get_server_api()
    response = requests.post(f"{server_api}/imports", json=import_data)
    return response.json()["data"]["import_id"]
