from flask.testing import FlaskClient
from requests import get, post
from requests.auth import HTTPBasicAuth

from eNMS.database.functions import fetch_all

from tests.test_base import check_pages


@check_pages("table/device")
def test_rest_api_basic(user_client: FlaskClient) -> None:
    number_of_devices = len(fetch_all("Device"))
    post(
        "http://192.168.105.2:5000/rest/instance/device",
        json={"name": "new_router", "model": "Cisco"},
        auth=HTTPBasicAuth("admin", "admin"),
    )
    assert len(fetch_all("Device")) == number_of_devices + 1
    result = get(
        "http://192.168.105.2:5000/rest/instance/device/Washington",
        auth=HTTPBasicAuth("admin", "admin"),
    ).json()
    assert result["model"] == "Arista"
    post(
        "http://192.168.105.2:5000/rest/instance/device",
        json={"name": "Washington", "model": "Cisco"},
        auth=HTTPBasicAuth("admin", "admin"),
    )
    result = get(
        "http://192.168.105.2:5000/rest/instance/device/Washington",
        auth=HTTPBasicAuth("admin", "admin"),
    ).json()
    assert result["model"] == "Cisco"
    result = get(
        "http://192.168.105.2:5000/rest/instance/service/get_facts",
        auth=HTTPBasicAuth("admin", "admin"),
    ).json()
    assert result["description"] == "Getter: get_facts"
    number_of_workflows = len(fetch_all("Workflow"))
    result = post(
        "http://192.168.105.2:5000/rest/instance/workflow",
        json={"name": "new_workflow", "description": "New"},
        auth=HTTPBasicAuth("admin", "admin"),
    ).json()
    assert (
        result["description"] == "New"
        and len(fetch_all("Workflow")) == number_of_workflows + 1
    )
