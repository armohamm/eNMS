============
What is eNMS
============

eNMS is a vendor-agnostic NMS designed for building workflow-based network automation solutions.

.. image:: /_static/base/enms.png
   :alt: eNMS Introduction
   :align: center

It encompasses the following aspects of network automation:
  - **Configuration Management Service**: Commit / Rollback of a configuration with Napalm or Netmiko.
  - **Ansible Service**: Sending and managing Ansible playbooks.
  - **ReST Service**: Sending a ReST call (GET/POST/UPDATE/DELETE) with variable URL and payload.
  - **Custom Services**: Any python script can be integrated into the web UI. If the script takes input parameters, a form will be automatically generated.
  - **Workflows**: Services can be combined together graphically in a workflow.
  - **Scheduling**: Services and workflows can be scheduled to start at a later time, or run periodically.
  - **Event-driven automation**: Services and workflows can be triggered by an external event (ReST call or Syslog message).

.. image:: /_static/base/workflow.gif
   :alt: eNMS workflow system
   :align: center

Main features
-------------
    
Creation of the network
***********************

Devices and links can be created either one by one, or all at once by importing an Excel spreadsheet.
Once created, all objects are displayed in a sortable and searchable table, from which they can be edited and deleted.
A dashboard provides a graphical overview of all objects with dynamic charts.

.. image:: /_static/base/inventory.png
   :alt: Inventory
   :align: center

.. image:: /_static/base/dashboard.png
   :alt: Dashboard
   :align: center

Network visualization
*********************

Once created, eNMS can display your network geographically on a 2D or 3D world map (with the tile layer of your choice: Open Street Map, Google Map...):
  - Network View: each device is displayed on the map at its GPS coordinates.

  .. image:: /_static/base/enms.png
    :alt: Geographical View
    :align: center

  - Site View: colocated devices can be grouped into geographical sites (building, campus, ...). eNMS then uses a force-based algorithm to display a "logical" view of the site's internal devices.

.. image:: /_static/views/site_view/site_view.png
   :alt: Logical view
   :align: center

You can click on a device to display its properties or start a Web SSH terminal session.

Service creation
****************

eNMS comes with a number of "default services" leveraging libraries such as `ansible`, `requests`, `netmiko`, `napalm`  to perform simple automation tasks. However, absolutely any python script can be turned into a "service".
If your python script takes input parameters, eNMS will automatically generate a form in the web UI.

To generate a form that matches your service, eNMS will perform the following conversion:
  - python `string` -> Text box (single line or multiline)
  - python `list` -> Drop-down list (single or multiselect).
  - python `bool` -> Checkbox.
  - python `dict` -> Text box expecting a dictionary.

.. image:: /_static/base/form_generation.png
  :alt: Form Generation
  :align: center

Once created, you can have as many instances of your service as you need. Service instances can be executed, edited and deleted from the web UI.

.. image:: /_static/base/service_management.png
  :alt: Service Management
  :align: center

Workflows
*********

Services (and other Workflows) can be combined into a single workflow.
Within a workflow, services can be connected with two edge types: `Success` edge and `Failure` edge. The `Success` edge (versus `Failure` edge) indicates which path to follow in the graph if the source service is successfully executed (versus failed).
A workflow keeps track of a `payload` dictionary, such that when a service starts, it has access to the results of all previously executed services.
When a workflow is executed, its status will be updated in real-time on the web UI.

.. image:: /_static/base/workflow.png
  :alt: Workflow Builder
  :align: center

Scheduling
**********

While services and workflows can be run directly and immediately from the web UI, you can also schedule them to run at a later time, or periodically by defining a frequency, a start date and an end date. All scheduled tasks are displayed in a calendar.

.. image:: /_static/base/calendar.png
  :alt: Calendar
  :align: center

Configuration Management
************************

eNMS can work as a network device configuration backup tool and replace Oxidized/Rancid with the following features:
  - Poll network elements; download configurations when they change
  - Easily view the current configuration of a device in the inventory
  - Search for any text in any configuration
  - View differences between various revisions of a configuration
  - Download device configuration to a local text file
  - Use the ReST API support to return a specified device’s configuration
  - Export all device configurations to a remote Git repository (e.g. Gitlab)

.. image:: /_static/base/configuration_management.png
  :alt: Configuration Management
  :align: center

Event-driven automation
***********************

Event-driven automation in eNMS has two aspects:
  - eNMS has a ReST API that can be used to create, update and delete any type of objects (services, workflows, tasks), but also to trigger the execution of a service or a workflow. 
  - eNMS can be configured as a Syslog server: all logs are stored in the database, and rules can be created to trigger the execution of a service or a workflow upon receiving a log matched by the rule.

Application stack
-----------------

eNMS is built on the :guilabel:`Flask` Python framework and utilizes either a :guilabel:`SQLite`, :guilabel:`MySQL`, or a :guilabel:`PostgreSQL` database. It runs as a WSGI service behind your choice of HTTP server.

+----------------------------------------+------------------------------------+
|Function                                |Component                           |
+========================================+====================================+
|HTTP Service                            |nginx or Apache                     |
+----------------------------------------+------------------------------------+
|WSGI Service                            |gunicorn or uWSGI                   |
+----------------------------------------+------------------------------------+
|Application                             |Flask/Python 3.6+                   |
+----------------------------------------+------------------------------------+
|Database                                |SQLite or PostgreSQL                |
+----------------------------------------+------------------------------------+
|Credentials storage                     |Hashicorp vault                     |
+----------------------------------------+------------------------------------+
|WebSSH connection                       |GoTTY                               |
+----------------------------------------+------------------------------------+