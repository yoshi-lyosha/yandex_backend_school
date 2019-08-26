import pytest
import requests

from app.tests.utils import get_server_api
from app.tests.api_functions import import_citizens
from app.tests.api.v1.tests_configs import get_citizens_gifts_config as c
from app.tests.api.v1.tests_configs import import_citizens_config as import_c


endpoint = "/imports/{import_id}/citizens/birthdays"


@pytest.fixture(scope="session")
def import_fixture():
    return import_citizens(import_c.simple_import_data)


def test_get_presents(import_fixture):
    import_id = import_fixture
    server_api = get_server_api()
    response = requests.get(f"{server_api}{endpoint.format(import_id=import_id)}")

    assert response.status_code == 200
    assert response.json() == c.simple_presents_response


def test_wrong_import_id():
    import_id = -1
    server_api = get_server_api()
    response = requests.get(f"{server_api}{endpoint.format(import_id=import_id)}")

    assert response.status_code == 200
    assert response.json() == c.incorrect_request_response
