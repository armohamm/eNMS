from sqlalchemy import Column, ForeignKey, Integer, String
from typing import Optional
from wtforms import HiddenField, IntegerField, StringField

from eNMS.database import SMALL_STRING_LENGTH
from eNMS.forms.automation import ServiceForm
from eNMS.models.automation import Job, Service
from eNMS.models.inventory import Device


class ConfigureBgpService(Service):

    __tablename__ = "ConfigureBgpService"

    id = Column(Integer, ForeignKey("Service.id"), primary_key=True)
    has_targets = True
    local_as = Column(Integer, default=0)
    loopback = Column(String(SMALL_STRING_LENGTH), default="")
    loopback_ip = Column(String(SMALL_STRING_LENGTH), default="")
    neighbor_ip = Column(String(SMALL_STRING_LENGTH), default="")
    remote_as = Column(Integer, default=0)
    vrf_name = Column(String(SMALL_STRING_LENGTH), default="")
    driver = "ios"

    __mapper_args__ = {"polymorphic_identity": "ConfigureBgpService"}

    def job(self, payload: dict, device: Device, parent: Optional[Job] = None) -> dict:
        napalm_connection = self.napalm_connection(device, parent)
        config = f"""
            ip vrf {self.vrf_name}
            rd {self.local_as}:235
            route-target import {self.local_as}:410
            route-target export {self.local_as}:400
            maximum route 10000 80
            interface {self.loopback}
            ip vrf forwarding {self.vrf_name}
            ip address {self.loopback_ip} 255.255.255.255
            router bgp {self.local_as}
            address-family ipv4 vrf {self.vrf_name}
            network {self.loopback_ip} mask 255.255.255.255
            neighbor {self.neighbor_ip} remote-as {self.remote_as}
            neighbor {self.neighbor_ip} activate
            neighbor {self.neighbor_ip} send-community both
            neighbor {self.neighbor_ip} as-override
            exit-address-family
        """
        config = "\n".join(config.splitlines())
        self.logs.append(f"Pushing BGP configuration on {device.name} (Napalm)")
        getattr(napalm_connection, "load_merge_candidate")(config=config)
        napalm_connection.commit_config()
        return {"success": True, "result": f"Config push ({config})"}


class ConfigureBgpForm(ServiceForm):
    form_type = HiddenField(default="ConfigureBgpService")
    local_as = IntegerField("Local AS", default=0)
    loopback = StringField("Loopback", default="Lo42")
    loopback_ip = StringField("Loopback IP")
    neighbor_ip = StringField("Neighbor IP")
    remote_as = IntegerField("Remote AS")
    vrf_name = StringField("VRF Name")
