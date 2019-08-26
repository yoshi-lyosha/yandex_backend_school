from datetime import date, timedelta

import pytest
import requests

from app.tests.utils import get_server_api, IntValue
from app.tests.api.v1.tests_configs import import_citizens_config as c


endpoint = "imports"


def test_base_import():
    server_api = get_server_api()
    response = requests.post(f"{server_api}/{endpoint}", json=c.simple_import_data)
    assert response.status_code == 200
    assert response.json() == {"data": {"import_id": IntValue()}}


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
def test_wrong_cases(case_name, field, wrong_value):
    server_api = get_server_api()
    citizen_to_import = c.citizen_template.copy()
    citizen_to_import[field] = wrong_value
    data = {"citizens": [citizen_to_import]}
    response = requests.post(f"{server_api}/{endpoint}", json=data)
    assert response.status_code == 400
