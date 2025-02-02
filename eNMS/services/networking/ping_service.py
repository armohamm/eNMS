from socket import error, gaierror, socket, timeout
from subprocess import check_output
from sqlalchemy import Column, ForeignKey, Integer, String
from subprocess import CalledProcessError
from typing import Optional
from wtforms import HiddenField, IntegerField, SelectField, StringField

from eNMS.database import SMALL_STRING_LENGTH
from eNMS.forms.automation import ServiceForm
from eNMS.models.automation import Job, Service
from eNMS.models.inventory import Device


class PingService(Service):

    __tablename__ = "PingService"

    id = Column(Integer, ForeignKey("Service.id"), primary_key=True)
    has_targets = True
    protocol = Column(String(SMALL_STRING_LENGTH), default="")
    ports = Column(String(SMALL_STRING_LENGTH), default="")
    count = Column(Integer, default=5)
    timeout = Column(Integer, default=2)
    ttl = Column(Integer, default=0)
    packet_size = Column(Integer, default=0)

    __mapper_args__ = {"polymorphic_identity": "PingService"}

    def job(self, payload: dict, device: Device, parent: Optional[Job] = None) -> dict:
        if self.protocol == "ICMP":
            command = ["ping"]
            for x, property in (
                ("c", "count"),
                ("W", "timeout"),
                ("t", "ttl"),
                ("s", "packet_size"),
            ):
                value = getattr(self, property)
                if value:
                    command.extend(f"-{x} {value}".split())
            command.append(device.ip_address)
            self.logs.append(f"Running ping ({command})")
            try:
                output = check_output(command).decode().strip().splitlines()
            except CalledProcessError:
                return {"success": False, "error": "Device not pingable"}
            total = output[-2].split(",")[3].split()[1]
            loss = output[-2].split(",")[2].split()[0]
            timing = output[-1].split()[3].split("/")
            return {
                "success": True,
                "result": {
                    "probes_sent": self.count,
                    "packet_loss": loss,
                    "rtt_min": timing[0],
                    "rtt_max": timing[2],
                    "rtt_avg": timing[1],
                    "rtt_stddev": timing[3],
                    "total rtt": total,
                },
            }
        else:
            result = {}
            for port in map(int, self.ports.split(",")):
                s = socket()
                s.settimeout(self.timeout)
                try:
                    connection = not s.connect_ex((device.ip_address, port))
                except (gaierror, timeout, error):
                    connection = False
                finally:
                    s.close()
                result[port] = connection
            return {"success": all(result.values()), "result": result}


class PingServiceForm(ServiceForm):
    form_type = HiddenField(default="PingService")
    protocol = SelectField(choices=(("ICMP", "ICMP Ping"), ("TCP", "TCP Ping")))
    ports = StringField()
    count = IntegerField(default=5)
    timeout = IntegerField(default=2)
    ttl = IntegerField(default=0)
    packet_size = IntegerField(default=0)
