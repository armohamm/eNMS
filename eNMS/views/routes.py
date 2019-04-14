from flask import request
from typing import Union

from eNMS.functions import fetch, fetch_all, get, get_one, post
from eNMS.properties import subtype_sizes, link_subtype_to_color
from eNMS.inventory.forms import DeviceAutomationForm, PoolRestrictionForm
from eNMS.views import bp


@get(bp, "/<view_type>_view", "View")
def view(view_type: str) -> dict:
    parameters = get_one("Parameters").serialized
    return dict(
        template="geographical_view",
        parameters=parameters,
        device_automation_form=DeviceAutomationForm(request.form),
        subtype_sizes=subtype_sizes,
        link_colors=link_subtype_to_color,
        pool_restriction_form=PoolRestrictionForm(request.form),
        view_type=view_type,
    )


@post(bp, "/get_logs/<int:device_id>", "View")
def get_logs(device_id: int) -> Union[str, bool]:
    device_logs = [
        log.content
        for log in fetch_all("Log")
        if log.source == fetch("Device", id=device_id).ip_address
    ]
    return "\n".join(device_logs) or True
