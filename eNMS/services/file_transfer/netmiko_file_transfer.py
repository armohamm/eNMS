from netmiko import file_transfer
from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String
from typing import Optional
from wtforms import (
    BooleanField,
    FloatField,
    HiddenField,
    IntegerField,
    SelectField,
    StringField,
)
from wtforms.validators import InputRequired

from eNMS.controller import controller
from eNMS.database import SMALL_STRING_LENGTH
from eNMS.forms.automation import ServiceForm
from eNMS.models.automation import Job, Service
from eNMS.models.inventory import Device


class NetmikoFileTransferService(Service):

    __tablename__ = "NetmikoFileTransferService"

    id = Column(Integer, ForeignKey("Service.id"), primary_key=True)
    has_targets = True
    privileged_mode = Column(Boolean, default=False)
    source_file = Column(String(SMALL_STRING_LENGTH), default="")
    destination_file = Column(String(SMALL_STRING_LENGTH), default="")
    direction = Column(String(SMALL_STRING_LENGTH), default="")
    disable_md5 = Column(Boolean, default=False)
    driver = Column(String(SMALL_STRING_LENGTH), default="")
    use_device_driver = Column(Boolean, default=True)
    file_system = Column(String(SMALL_STRING_LENGTH), default="")
    inline_transfer = Column(Boolean, default=False)
    overwrite_file = Column(Boolean, default=False)
    fast_cli = Column(Boolean, default=False)
    timeout = Column(Integer, default=1)
    global_delay_factor = Column(Float, default=1.0)

    __mapper_args__ = {"polymorphic_identity": "NetmikoFileTransferService"}

    def job(self, payload: dict, device: Device, parent: Optional[Job] = None) -> dict:
        netmiko_connection = self.netmiko_connection(device, parent)
        self.logs.append("Transferring file {self.source_file} on {device.name}")
        source = self.sub(self.source_file, locals())
        destination = self.sub(self.destination_file, locals())
        transfer_dict = file_transfer(
            netmiko_connection,
            source_file=source,
            dest_file=destination,
            file_system=self.file_system,
            direction=self.direction,
            overwrite_file=self.overwrite_file,
            disable_md5=self.disable_md5,
            inline_transfer=self.inline_transfer,
        )
        return {"success": True, "result": transfer_dict}


class NetmikoFileTransferForm(ServiceForm):
    form_type = HiddenField(default="NetmikoFileTransferService")
    privileged_mode = BooleanField("Privileged mode (run in enable mode or as root)")
    source_file = StringField(validators=[InputRequired()])
    destination_file = StringField(validators=[InputRequired()])
    file_system = StringField()
    direction = SelectField(choices=(("put", "Upload"), ("get", "Download")))
    driver = SelectField(choices=controller.NETMIKO_SCP_DRIVERS)
    disable_md5 = BooleanField()
    use_device_driver = BooleanField()
    inline_transfer = BooleanField()
    overwrite_file = BooleanField()
    fast_cli = BooleanField()
    timeout = IntegerField(default=1)
    global_delay_factor = FloatField(default=1.0)
