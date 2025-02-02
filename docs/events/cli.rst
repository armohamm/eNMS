=============
CLI interface
=============

eNMS has a CLI interface with the following operations:

Fetch an object from the database
----------------------------------

General syntax: `flask fetch object_type object_name`
Example: `flask fetch device Washington`

Modify the properties of an object
----------------------------------

General syntax: `flask update object type 'object_properties'` where `object_properties` is a JSON dictionary that contains the name of the object, and the property to update. 
Example: `flask update device '{"name": "Aserver", "description": "test"}'`

Delete an object from the database
----------------------------------

General syntax: `flask delete object_type object_name`
Example: `flask delete device Washington`

Run a service
-------------

General syntax: `flask start service_name --devices list_of_devices --payload 'payload'` where:
- list_of_devices is a list of device name separated by commas.
- payload is a JSON dictionary.
Both devices and payload are optional parameters.

Example: `flask start get_facts`
Example 2: `flask start get_facts --devices Washington,Denver`
Example 3: `flask start a_service --payload '{"a": "b"}'`
Example 4: `flask start get_facts --devices Washington,Denver --payload '{"a": "b"}'`
