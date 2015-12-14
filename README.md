# infrastructure-repository
The infrastructure repository is a tool that provides infrastructure related information collected from Openstack and Opendaylight. This subsystem is comprised of three key elements:

* EPA controller
* EPA Agent
* API

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
The EPA Agent run on each machine of the cluster. It should be configured to run on the boot of the machine. 
