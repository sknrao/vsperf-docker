This directory contains the source from Dovetail/Dovetail-webportal project.
Once the results container is deployed, please run the python script as follows, to ensure that results can be pushed and queried correctly.
```sh
python init_db.py host_ip_address testapi_port
```
For example, if the host on which the container is running is 10.10.120.22, and container is exposing 8000 as the port, the command should be:
```sh
python init_db.py 10.10.120.22 8000
```
