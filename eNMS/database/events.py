from flask_login import current_user
from sqlalchemy import Boolean, event, Float, inspect, Integer, PickleType
from sqlalchemy.engine.base import Connection
from sqlalchemy.ext.declarative.api import DeclarativeMeta
from sqlalchemy.orm.mapper import Mapper
from typing import Any

from eNMS.controller import controller
from eNMS.models import model_properties, models, property_types, relationships
from eNMS.database.base import Base
from eNMS.database.functions import fetch_all
from eNMS.models.automation import Workflow
from eNMS.properties.database import dont_track_changes


@event.listens_for(Base, "mapper_configured", propagate=True)
def model_inspection(mapper: Mapper, cls: DeclarativeMeta) -> None:
    name = cls.__tablename__
    for col in cls.__table__.columns:
        model_properties[name].append(col.key)
        if col.type == PickleType and isinstance(col.default.arg, list):
            property_types[col.key] = "list"
        else:
            column_type = {
                Boolean: "bool",
                Integer: "int",
                Float: "float",
                PickleType: "dict",
            }.get(type(col.type), "str")
            if col.key not in property_types:
                property_types[col.key] = column_type
    if hasattr(cls, "parent_cls"):
        model_properties[name].extend(model_properties[cls.parent_cls])
    if "Service" in name and name != "Service":
        model_properties[name].extend(model_properties["Service"])
    model = {name: cls, name.lower(): cls}
    models.update(model)
    for relation in mapper.relationships:
        property = str(relation).split(".")[1]
        relationships[name][property] = {
            "model": relation.mapper.class_.__tablename__,
            "list": relation.uselist,
        }


def configure_events() -> None:
    @event.listens_for(Base, "init", propagate=True)
    def log_instance_creation(target: Base, args: tuple, kwargs: dict) -> None:
        if "type" not in target.__dict__:
            return
        controller.log(
            "info",
            (
                f"User '{getattr(current_user, 'name', 'admin')}' CREATED "
                f"{target.__dict__['type']} '{kwargs['name']}'"
            ),
        )

    @event.listens_for(Base, "before_delete", propagate=True)
    def log_instance_deletion(
        mapper: Mapper, connection: Connection, target: Base
    ) -> None:
        controller.log(
            "info",
            (
                f"User '{getattr(current_user, 'name', 'admin')}' DELETED "
                f"{target.type} '{target.name}'."
            ),
        )

    @event.listens_for(Base, "after_update", propagate=True)
    def log_instance_update(
        mapper: Mapper, connection: Connection, target: Base
    ) -> None:
        state, changes = inspect(target), []
        for attr in state.attrs:
            hist = state.get_history(attr.key, True)
            if not hist.has_changes() or attr.key in dont_track_changes:
                continue
            changes.append(f"{attr.key}: {hist.deleted} => {hist.added}")
        if changes:
            controller.log(
                "info",
                (
                    f"User '{getattr(current_user, 'name', 'admin')}' UPDATED "
                    f"{target.type} '{target.name}' ({' | '.join(changes)})."
                ),
            )

    @event.listens_for(Workflow.name, "set")
    def workflow_name_update(
        workflow: Base, new_name: str, old_name: str, *args: Any
    ) -> None:
        for job in fetch_all("Job"):
            if old_name in job.positions:
                job.positions[new_name] = job.positions.pop(old_name)
