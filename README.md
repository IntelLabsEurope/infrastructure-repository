# Infrastructure Repository

The infrastructure repository is a tool that provides infrastructure related information collected from Openstack and Opendaylight. This subsystem is comprised of three key elements:

* EPA controller
* EPA Agent
* API

In the following the procedure to install and configure the tool on Ubuntu Machines. The same procedure has been tested on Fedora replacing apt-get with yum.

### Prerequisites
* Openstack Kilo Release
* Opendaylight Lithium Release
* Neo4j Database

### EPA Controller
Collect the information and store them in Neo4j DB. 
Information are collected listening the Openstack notifications, querying the Openstack DBs and listening the agents notifications queue.

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
Provide required information in a configuration file.
A sample is provided in config/epa_controller.cfg
Run the controller with the following command:
````
infrastructure_repo -c <path/to/configuration/file>
```

### EPA Agent
The EPA Agent run on each machine of the cluster. It collects hardware information about the machine where it is running and sends it to the controller. The agent should be launched after the Controller is up and running.

##### Installation
Copy a priv key of the controller to the machine where you want to run the agent.
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

### API
The API component exposes an OCCI interface to the information stored in one or more the infrastructure repositories (each one called Point of Presence (PoP)).
##### Installation
In the root directory:
````python
pip install -r requirements.txt
python setup.py install
```

##### Run API component / Middleware
Provide required information in a configuration file.
A sample is provided in config/middleware.cfg
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
To see the list of PoPs navigate to:
http://<middleware_ip>:<middleware_port>/pop/

Click on the PoP stored and list the VMs of the PoP navigating to:
```
http://<MIDDLEWARE_IP>:<MIDDLEWARE_PORT>/pop/<POP_ID>/vm/
```
