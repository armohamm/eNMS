from collections import defaultdict
from flask import request
from flask_login import current_user
from flask_wtf import FlaskForm
from werkzeug.datastructures import ImmutableMultiDict
from wtforms import HiddenField, SelectField, StringField
from wtforms.fields.core import UnboundField
from wtforms.form import FormMeta

from eNMS.forms.fields import field_types, MultipleInstanceField
from eNMS.models import property_types
from eNMS.properties import field_conversion, property_names
from eNMS.properties.table import filtering_properties

form_actions = {}
form_classes = {}
form_properties: dict = defaultdict(dict)
form_templates = {}


class MetaForm(FormMeta):
    def __new__(cls: type, name: str, bases: tuple, attrs: dict) -> FlaskForm:
        form: FlaskForm = type.__new__(cls, name, bases, attrs)
        if name == "BaseForm":
            return form
        form_type = form.form_type.kwargs["default"]
        form_classes[form_type] = form
        form_templates[form_type] = getattr(form, "template", "base")
        form_actions[form_type] = getattr(form, "action", None)
        properties = {
            field_name: field_types[field.field_class]
            for field_name, field in attrs.items()
            if isinstance(field, UnboundField) and field.field_class in field_types
        }
        property_names.update(
            {
                field_name: field.args[0]
                for field_name, field in attrs.items()
                if isinstance(field, UnboundField) and field.args
            }
        )
        form_properties[form_type].update(properties)
        property_types.update(properties)
        for base in form.__bases__:
            if not hasattr(base, "form_type"):
                continue
            base_form_type = base.form_type.kwargs["default"]
            if base_form_type == "service":
                form.service_fields = list(properties)
            if getattr(base, "abstract_service", False):
                form.service_fields.extend(form_properties[base_form_type])
            form_properties[form_type].update(form_properties[base_form_type])
        return form


class BaseForm(FlaskForm, metaclass=MetaForm):
    pass


def form_postprocessing(form: ImmutableMultiDict) -> dict:
    data = {**form.to_dict(), **{"user": current_user}}
    if request.files:
        data["file"] = request.files["file"]
    for property, field_type in form_properties[form.get("form_type")].items():
        if field_type in ("object-list", "multiselect"):
            data[property] = form.getlist(property)
        elif field_type == "bool":
            data[property] = property in form
        elif field_type in field_conversion and property in data:
            data[property] = field_conversion[field_type](form[property])
    return data


def filtering_form_generator() -> None:
    for table, properties in filtering_properties.items():
        kwargs = {}
        if table in ("device", "link", "configuration"):
            kwargs["pools"] = MultipleInstanceField("Pools", instance_type="Pool")
        type(
            f"{table.capitalize()}FilteringForm",
            (BaseForm,),
            {
                "template": "filtering",
                "properties": list(kwargs) + properties,
                "form_type": HiddenField(default=f"{table}_filtering"),
                **{
                    **{property: StringField() for property in properties},
                    **{
                        f"{property}_filter": SelectField(
                            choices=(
                                ("inclusion", "Inclusion"),
                                ("equality", "Equality"),
                                ("regex", "Regular Expression"),
                            )
                        )
                        for property in properties
                    },
                    **kwargs,
                },
            },
        )


filtering_form_generator()


import eNMS.forms.inventory  # noqa: F401
