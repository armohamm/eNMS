from wtforms import BooleanField, HiddenField, IntegerField, SelectField, StringField

from eNMS.forms import BaseForm
from eNMS.forms.fields import DateField, MultipleInstanceField, InstanceField


class DeviceAutomationForm(BaseForm):
    form_type = HiddenField(default="device_automation")
    jobs = MultipleInstanceField("Jobs", instance_type="Job")


class JobForm(BaseForm):
    template = "object"
    form_type = HiddenField(default="job")
    id = HiddenField()
    type = StringField("Service Type")
    name = StringField("Name")
    description = StringField("Description")
    devices = MultipleInstanceField("Devices", instance_type="Device")
    multiprocessing = BooleanField("Multiprocessing")
    max_processes = IntegerField("Maximum number of processes", default=50)
    credentials = SelectField(
        "Credentials",
        choices=(("device", "Device Credentials"), ("user", "User Credentials")),
    )
    pools = MultipleInstanceField("Pools", instance_type="Pool")
    waiting_time = IntegerField("Waiting time (in seconds)", default=0)
    send_notification = BooleanField("Send a notification")
    send_notification_method = SelectField(
        "Notification Method",
        choices=(
            ("mail_feedback_notification", "Mail"),
            ("slack_feedback_notification", "Slack"),
            ("mattermost_feedback_notification", "Mattermost"),
        ),
    )
    display_only_failed_nodes = BooleanField("Display only Failed Devices")
    mail_recipient = StringField("Mail Recipients (separated by comma)")
    number_of_retries = IntegerField("Number of retries", default=0)
    time_between_retries = IntegerField("Time between retries (in seconds)", default=10)
    vendor = StringField("Vendor")
    operating_system = StringField("Operating System")


class ServiceForm(JobForm):
    template = "service"
    form_type = HiddenField(default="service")


class WorkflowForm(JobForm):
    template = "workflow"
    form_type = HiddenField(default="workflow")


class JobFilteringForm(BaseForm):
    action = "filter"
    form_type = HiddenField(default="job filtering")
    name = StringField("Name")
    type = StringField("Service Type")
    description = StringField("Description")
    creator = StringField("Creator")
    max_processes = StringField("Maximum number of processes")
    credentials = StringField("Credentials")
    waiting_time = StringField("Waiting Time")
    send_notification_method = StringField("Notification Method")
    mail_recipient = StringField("Mail Recipient")
    number_of_retries = StringField("Number of retries")
    time_between_retries = StringField("Time between retries (in seconds)")


class ServiceFilteringForm(JobFilteringForm):
    form_type = HiddenField(default="service_filtering")


class WorkflowFilteringForm(JobFilteringForm):
    form_type = HiddenField(default="workflow_filtering")


class CompareResultsForm(BaseForm):
    template = "results"
    form_type = HiddenField(default="results")
    display = SelectField("Version to display", choices=())
    compare_with = SelectField("Compare Against", choices=())


class AddJobsForm(BaseForm):
    form_type = HiddenField(default="add_jobs")
    add_jobs = MultipleInstanceField("Add jobs", instance_type="Job")


class ServiceTableForm(BaseForm):
    form_type = HiddenField(default="service_table")
    services = SelectField(choices=())


class WorkflowBuilderForm(BaseForm):
    form_type = HiddenField(default="workflow_builder")
    workflow = InstanceField("Workflow", instance_type="Workflow")


def configure_form(cls: BaseForm) -> BaseForm:
    cls.properties = ("origin", "name")
    for property in ("origin", "name"):
        setattr(cls, property, StringField(property))
        setattr(cls, property + "_regex", BooleanField("Regex"))
    return cls


@configure_form
class LogAutomationForm(BaseForm):
    form_type = HiddenField(default="logrule")
    id = HiddenField()
    name = StringField("Name")
    jobs = MultipleInstanceField("Jobs", instance_type="Job")


class TaskForm(BaseForm):
    template = "base"
    form_type = HiddenField(default="task")
    id = HiddenField()
    is_active = BooleanField("Is Active")
    name = StringField("Name")
    description = StringField("Description")
    start_date = DateField("Start Date")
    end_date = DateField("End Date")
    frequency = IntegerField("Frequency")
    frequency_unit = SelectField(
        "Frequency Unit",
        choices=(
            ("seconds", "Seconds"),
            ("minutes", "Minutes"),
            ("hours", "Hours"),
            ("days", "Days"),
        ),
    )
    crontab_expression = StringField("Crontab Expression")
    job = InstanceField("Job", instance_type="Job")
    scheduling_mode = SelectField(
        "Scheduling Mode",
        choices=(("standard", "Standard Scheduling"), ("cron", "Crontab Scheduling")),
    )
