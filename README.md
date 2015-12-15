# Infrastructure Repository

The infrastructure repository is a tool that provides centralized collection and persistence of infrastructure related information available from an infrastructure virtualization and management layer build with open source components including OpenStack and OpenDaylight. This subsystem is comprised of three key elements:

* EPA controller
* EPA Agent
* API Middleware

The following outlines how to install and configure the tool on Ubuntu machines. The same procedure has also been tested on Fedora which requires replacing apt-get with yum.

### Prerequisites
* OpenStack (two versions currently supported Branch: OpenStack/Kilo, Branch: OpenStack/Liberty)
* OpenDaylight Lithium Release
* Neo4j Database

### EPA Controller
This component is responsible for collecting infrastructure information and storing the information in a Neo4j DB. 
Infrastructure related information is collected by listening to OpenStack notifications, querying the OpenStack services DBs and from updates received from EPA agents running on compute nodes within a NFVI-PoP.

##### Installation
Install Python Mysql Connector
```
apt-get install python-mysql.connector
```
In the root directory:
````python
pip install -r requirements.txt
python setup.py install
````
##### Run EPA Controller
First you must edit the EPA Controller configuration file with your specific deployment details.
A sample is provided in config/epa_controller.cfg.

Run the controller with the following command:
````
infrastructure_repo -c <path/to/configuration/file>
```

### EPA Agent
An EPA Agent runs on each compute node within an NFVI-PoP. It collects hardware information from the compute node where it is running and sends it to the controller. The agent should be launched after the Controller is up and running.

##### Installation
Copy a private key of the controller to the machine where you want to run the agent.
Install hwloc:
````
apt-get install hwloc 
````
Provide the information required by the agent in the configuration file. A sample can be found epa_agent/agent.cfg
Install required packages:
````
pip install pika
```
Run the agent:
````
python agent.py -c </path/to/the/configuration/file/>
```

### API Middleware
The API middleware component exposes an OCCI compliant interface to consuming functions which require access to infrastructure related information stored in one or more infrastructure repositories (each one called Point of Presence (PoP)).
##### Installation
In the root directory:
````python
pip install -r requirements.txt
python setup.py install
```

##### Run API Middleware component
Provide required information in a configuration file.
A sample is provided in config/middleware.cfg.

Run the middleware with the following command:
````
infrastructure_repo_api -c <path/to/configuration/file>
```

##### Add a new PoP
Add a new PoP with the same name as the one used in the Epa Controller configuration file.
Es.
````
curl -X POST http://<MIDDLEWARE_IP>:<MIDDLEWARE_PORT>/pop/ --header "Accept: application/occi+json" --header "Content-Type: text/occi" --header 'Category: pop; scheme="http://schemas.ogf.org/occi/epa#"; class="kind"' 
-d  'X-OCCI-Attribute: occi.epa.pop.graph_db_url="http://usr:password@<NEO4J_IP>:7474/db/data/" X-OCCI-Attribute: occi.epa.pop.odl_url="http://<ODL_IP>:8181/restconf/operational/"  X-OCCI-Attribute: occi.epa.pop.odl_name="admin" X-OCCI-Attribute: occi.epa.pop.odl_password="admin"' X-OCCI-Attribute: occi.epa.pop.name="GR-ATH-0001" 
X-OCCI-Attribute: occi.epa.pop.lat=37.9997104  X-OCCI-Attribute: occi.epa.pop.lon=23.8168182'
```

To see the list of available PoPs navigate to:
```
http://<MIDDLEWARE_IP>:<MIDDLEWARE_PORT>/pop/
```

Click on the PoP stored and list the VMs of the PoP navigating to:
```
http://<MIDDLEWARE_IP>:<MIDDLEWARE_PORT>/pop/<POP_ID>/vm/
```

### Suggestions:
To support the long term management of the EPA Controller and API Middleware components, [Supervisor ] (http://supervisord.org/) an open source solution for process monitoring and control is used.
