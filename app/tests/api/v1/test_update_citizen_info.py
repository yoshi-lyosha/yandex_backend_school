from datetime import date, timedelta

import pytest
import requests

from app.tests.utils import get_server_api
from app.tests.api_functions import import_citizens
from app.tests.api.v1.tests_configs import update_citizen_info_config as c
from app.tests.api.v1.tests_configs import import_citizens_config as import_c


endpoint = "/imports/{import_id}/citizens/{citizen_id}"


@pytest.fixture(scope="session")
def import_fixture():
    return import_citizens(import_c.simple_import_data)


def test_base_update(import_fixture):
    import_id = import_fixture
    server_api = get_server_api()
    response = requests.patch(
        f"{server_api}{endpoint.format(import_id=import_id, citizen_id=3)}",
        json=c.update_data,
    )

    citizen_after_update_template = import_c.simple_import_data["citizens"][2].copy()
    citizen_after_update_template.update(c.update_data)

    assert response.status_code == 200
    assert response.json()["data"] == citizen_after_update_template


def test_not_existent_user(import_fixture):
    import_id = import_fixture
    server_api = get_server_api()
    response = requests.patch(
        f"{server_api}{endpoint.format(import_id=import_id, citizen_id=69)}",
        json=c.update_data,
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}


@pytest.mark.parametrize(
    "case_name, field, wrong_value",
    [
        ("extra_value", "extra", "value"),
        ("inapropriate_gender", "gender", "transformer"),
        ("gender_incorrect_type", "gender", []),
        ("birth_date_incorrect_format", "birth_date", "228.14.88"),
        (
            "birth_date_greater_than_today",
            "birth_date",
            (date.today() + timedelta(69)).strftime("%d.%m.%Y"),
        ),
        ("town_incorrect_type", "town", []),
        ("town_invalid_lenght_1", "town", ""),
        ("town_invalid_lenght_2", "town", "a" * 257),
        ("street_incorrect_type", "street", []),
        ("building_incorrect_type", "building", []),
        ("apartment_incorrect_type", "apartment", []),
        ("apartment_invalid_value", "apartment", -1),
        ("name_incorrect_type", "name", []),
        ("relatives_wrong_type", "relatives", 420),
    ],
)
def test_wrong_cases(case_name, field, wrong_value, import_fixture):
    import_id = import_fixture
    server_api = get_server_api()
    citizen_to_update = c.update_data.copy()
    citizen_to_update[field] = wrong_value
    response = requests.patch(
        f"{server_api}{endpoint.format(import_id=import_id, citizen_id=3)}",
        json=citizen_to_update,
    )

    assert response.status_code == 400
