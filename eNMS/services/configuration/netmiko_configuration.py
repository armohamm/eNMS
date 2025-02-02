from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, Text
from typing import Optional
from wtforms import (
    BooleanField,
    FloatField,
    HiddenField,
    IntegerField,
    SelectField,
    StringField,
)
from wtforms.widgets import TextArea

from eNMS.controller import controller
from eNMS.database import LARGE_STRING_LENGTH, SMALL_STRING_LENGTH
from eNMS.forms.automation import ServiceForm
from eNMS.models.automation import Job, Service
from eNMS.models.inventory import Device


class NetmikoConfigurationService(Service):

    __tablename__ = "NetmikoConfigurationService"

    id = Column(Integer, ForeignKey("Service.id"), primary_key=True)
    has_targets = True
    content = Column(Text(LARGE_STRING_LENGTH), default="")
    privileged_mode = Column(Boolean, default=False)
    driver = Column(String(SMALL_STRING_LENGTH), default="")
    use_device_driver = Column(Boolean, default=True)
    fast_cli = Column(Boolean, default=False)
    timeout = Column(Integer, default=1.0)
    delay_factor = Column(Float, default=1.0)
    global_delay_factor = Column(Float, default=1.0)
    commit_configuration = Column(Boolean, default=False)
    exit_config_mode = Column(Boolean, default=True)
    strip_prompt = Column(Boolean, default=False)
    strip_command = Column(Boolean, default=False)
    config_mode_command = Column(String(SMALL_STRING_LENGTH), default="")

    __mapper_args__ = {"polymorphic_identity": "NetmikoConfigurationService"}

    def job(self, payload: dict, device: Device, parent: Optional[Job] = None) -> dict:
        netmiko_connection = self.netmiko_connection(device, parent)
        config = self.sub(self.content, locals())
        self.logs.append(f"Pushing configuration on {device.name} (Netmiko)")
        netmiko_connection.send_config_set(
            config.splitlines(),
            delay_factor=self.delay_factor,
            exit_config_mode=self.exit_config_mode,
            strip_prompt=self.strip_prompt,
            strip_command=self.strip_command,
            config_mode_command=self.config_mode_command,
        )
        if self.commit_configuration:
            netmiko_connection.commit()
        return {"success": True, "result": f"configuration OK {config}"}


class NetmikoConfigurationForm(ServiceForm):
    form_type = HiddenField(default="NetmikoConfigurationService")
    content = StringField(widget=TextArea(), render_kw={"rows": 5})
    privileged_mode = BooleanField("Privileged mode (run in enable mode or as root)")
    driver = SelectField(choices=controller.NETMIKO_DRIVERS)
    use_device_driver = BooleanField(default=True)
    fast_cli = BooleanField()
    timeout = IntegerField(default=10)
    delay_factor = FloatField(default=1.0)
    global_delay_factor = FloatField(default=1.0)
    commit_configuration = BooleanField()
    exit_config_mode = BooleanField()
    strip_prompt = BooleanField()
    strip_command = BooleanField()
    config_mode_command = StringField()
