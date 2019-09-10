VSPERF Client
--------------
VSPERF client is a simple python application, which can be used to work with interactive deploy and testcontrol containers.

============
Description
============

VSPERF client is used for both set-up of DUT-Host and TGen-Host as well as run the multiple tests. User can perform different operations by selecting the available options and their sub-options.

VSPERF client provides following options for User.

* Establish Connections
This option allow user to initialize the connections with DUT-Host and TGen-Host based on the credential provided in the vsperfclient.conf file.

* VSPERF Prerequisites Installation
After connection has established, user can perform installation of VSPERF and Collectd on DUT-Host, Traffic Generator(T-rex) on TGen-Host.

* Upload Configuration Files
Once set-up is done, User can upload Collectd configuration file on DUT-Host and T-Rex configuration file on TGen-Host.

* Manage System Configuration
User can manage hugepages of DUT-Host and Check VSPERF dependencies. User need to provide value for HpMax and HpRequested in vsperfclient.conf file.

* Run Test
After VSPERF Set-up is done, user can upload Vsperf test configuration file on DUT_Host. Further some, user must perform all sanity checks before running test. User does not able to start the Vsperf test until all sanity checks satisfied. This sanity check option contains following sub-options like to check VSPERF installed correctly, check Test Config's VNF path is available  on DUT-Host, check NIC PCIs is available on Traffic Generator, check installed Collectd, connection between DUT-Host and Traffic Generator Host, check CPU-allocation on DUT-host.User can check if DUT-Host is available for Test or not. If DUT-Host available for performing Vsperf test then user can start T-rex, start beats and start test.

* Test Status
After running test user can check whether their test completed successfully or failed. If user is running multiple test then they can identify the failed test name using this option.
User can also able to read the vsperf.conf file content they uploaded.

* Clean-Up
Once user completed test, VSPERF client provide option to remove everything from DUT-host or any specific content related with VSPERF.

=============================
How To Use
=============================

Prerequisites before running vsperf client
^^^^^^^^^^^^^^^^^^^^^
User must need to install grpcio, grpcio-tools and configparser for python3 environment. User can run the Vsperf client script with python3.

User have to provide credentials for DUT-Host and TGen-host, value for the number of hugepages(HpMax and HpRequested) and vsperf test name under Testcase section.

For Uploading the configuration files user have two choices
1.User can provide path in vsperfclient.conf file.
2.When running client ask for path use specific path where configuration file exist.

T-rex and collectd configuration file should be saved with trex_cfg.yaml and collectd.conf respectively. Test configuration file can be saved according to your preferences and reliability.

Firstly, user **must have to start the deployment/interactive container and testcontrol/interactive container which will run the servers on localhost port 50051 and 50052** respectively for vsperf client.

Run vsperf client
^^^^^^^^^^^^^^^^^^^^^
Locate and run the vsperf_client.py with python3.

[By default user does not require to make any changes in proto/vsperf.proto file to run the vsperf_client.py. However, if user want to add more APIs in current client they have to define them in proto/vsperf.proto file and use this command to make them usable for vsperf_client.py **python3 -m grpc_tools.protoc -I./ --python_out=. --grpc_python_out=. vsperf.proto**]
