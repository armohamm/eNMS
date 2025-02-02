============
Pools
============

Pools allow the user to create groups of objects. They can be used to filter the inventory tables and the view, but also to target an automation task to a specific subset of devices.
A pool is defined as a combination of values (or regular expressions) for the properties of an object (in the inventory). 

If the properties of an inventory object matches the pool properties (``any of them``, or ``all of them`` depending on your needs), the object will belong to the pool.

Pool Management
---------------

Pools can be created, updated, duplicated and deleted from the :guilabel:`Inventory / Pool Management` page, and they can be
edited to manually select Objects instead of using criteria based on properties to select them.

.. image:: /_static/inventory/pool_management/pool_management.png
   :alt: Pool Management
   :align: center

Additionally, a logical view force diagram of a pool is available using the ``Visualize`` button.

.. image:: /_static/inventory/pool_management/pool_visualization.png
   :alt: Pool Visualization
   :align: center

.. note:: When you add a new device A whose properties are matched by pool B, A is automatically added to B.

A first example
---------------

.. image:: /_static/inventory/pool_management/device_filtering.png
   :alt: Device Filtering
   :align: center

This pool enforces the following conditions:
 * name: ``node.*`` --- this regular expression matches all devices which name starts with ``node``.
 * type: ``Router|Switch`` --- matches routers and switches (devices which type is either ``Router``, or ``Switch``.
 * vendor: ``Cisco`` --- for this property, the regular expression box is not ticked. This means the value must be exactly ``Cisco``.

In summary, all ``Cisco`` ``routers or switches`` whose name begins with ``node`` will match these conditions, and they will be a member of the pool.

.. note:: All properties left with empty fields are simply ignored.

A pool of links
---------------

.. image:: /_static/inventory/pool_management/link_filtering.png
   :alt: Link filtering
   :align: center

This pool enforces the following conditions:
 * type: ``Ethernet link`` --- matches all Ethernet links.
 * source: ``bnet6`` --- matches all links whose source is the device ``bnet6``.

In summary, all ``Ethernet`` links starting from the device ``bnet6`` will be part of the pool.

Default pools
-------------

Three pools are created by default in eNMS:

- "All objects": a pool that matches all devices and links.
- "Devices only": matches all devices, no link.
- "Links only": matches all links, no device.

Never Update pools
------------------

Pools with manually selected objects (by selecting them using the Edit Objects button) need to have the 'Never Update' checkbox
selected. This prevents manually selected pools from being re-calculated based on pool criteria.  If the user wants to run against
a pool that has some criteria specified as well as some manually specified devices, it is advised to have 2 pools-one with the criteria
specified and another with the manually selected devices.  When running a job, multiple pools and multiple devices can be specified, and
the job will run against all specified objects.

Manual definition
-----------------

By default, the devices and links within a pool are determined based on the pool properties. However, the ``Edit objects`` button lets you define the pool devices and links by selecting them directly instead.
There are two ways to manually select the objects of a pool:

- By selecting them from a drop-down list.
- By copy/pasting a string made of devices' and links' names, separated by a comma.

.. image:: /_static/inventory/pool_management/manual_definition.png
   :alt: Manual definition of a pool
   :align: center

How Pools get Updated
---------------------

A pool is automatically updated by eNMS:

- after being created (as long as its 'never update' flag is not set)

All pools are updated (as long as their 'never update' flag is not set):

- when eNMS starts, or restarts
- when a device is manually added to the inventory
- when a device is modified
- after pulling or cloning the content from the git configuration repository
- when the `poller service` runs (service responsible for fetching all device configurations), all pools for which the device ``Current Configuration`` is not empty are updated (and only those).

Pools are manually updated:

- when you click on the update button of a pool in pool management
- when you click on the "update all pools" in pool management

Pools based on Configuration
----------------------------

Pools can be created by searching the configurations data collected from all of the devices, rather than just the Inventory parameters
for each device. Of course, configuration collection must be configured and allowed to run at least once before the configurations can
be searched for the pool.

Filter the view with a pool
---------------------------

Pools can be used as filters for the inventory devices and links tables, as well as the geographical views. You can click on the ``Filter Devices`` and ``Filter Links`` buttons to open the "Advanced Search" panel.
These panels both contain a ``Pools`` drop-down list (multiple selection) to filter objects in the view.

.. image:: /_static/inventory/pool_management/view_filter.png
   :alt: Pool filtering of the view
   :align: center

Use a pool as target of a Service or a Workflow
-----------------------------------------------

You can select multiple devices, as well as multiple pools as targets.

.. image:: /_static/inventory/pool_management/target_pool.png
   :alt: Use a pool as a target
   :align: center

Use a pool to restrict an eNMS user to a subset of objects
----------------------------------------------------------

From the :guilabel:`Admin / User Management` panel, you can select a pool used as a database filtering mechanism for a particular user.
All mechanisms and all pages in eNMS will be restricted to the objects of that pool for that particular user. The exception is Service and Workflows that have been already configured to run against particular set of devices and links. If those devices and links are outside of the pool that the user is restricted to, the user will still be able to see them.
