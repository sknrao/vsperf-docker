VSPERF Client
---------------------------------------------------------------------------------------------

============
Description
============

VSPERF client used for both set-up of DUT-Host and TGen-Host as well as run the multiple tests. User can perform different operations by selecting the available options and their sub-options.

VSPERF client provides following options for User.

* Establish Connections
This option allow user to initialize the connection with DUT-Host and TGen-Host based on the credential provided in the vsperfclient.conf file.

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

VSPERF Containers
------------------

============
deployment
============
User have two choices for deployment auto and interactive.

1. auto
^^^^^^^^^^^^^^^^^^^^^
This auto deployment container will do everything related with VSPERF set-up automatically. For example of installation of VSPERF, T-rex and collectd, upload T-rex and collectd configuration file on DUT-Host, start the t-rex traffic generator. If user find any failed or critical message in outputs, user should first correct those configuration and then run the testcontrol auto container to perform test.
Before installing vsperf and t-rex, container verify the installed vsperf and t-rex and if both are already installed then container will not repeat this process. 
User can modify the t-rex(trex_cfg.yaml)and collectd(collectd.conf) configuration files which will upload automatically.


Pre-Deployment Configuration
******************
1.User have to provide all the DUT-Host and Traffic generator related credentials and IP address in list.env.
2.Provide value for HUGEPAGE_MAX and HUGEPAGE_REQUESTED in list.env.
3.Provide option for sanity check YES or NO in list.env file which is optional.

Build
******************
Use **docker-compose build** command to build the container.

Run
******************
Run the container's service with **docker-compose run deploy** command.

Post-Deployment Configuration
******************
After running this container, if user find any failed or critical message in outputs then user should first correct those configuration and then run the testcontrol auto container to perform test.

2. interactive
^^^^^^^^^^^^^^^^^^^^^
This interactive container must run before using the vsperf client. It will just run the container and start the server for the vsperf client. Deployment interactive container handle all vsperf set-up related commands from vsperf client and perform the operation. Deployment interactive container running server on localhost port 50051.


Build
******************
Run **docker-compose build** command to build the container.

Run
******************
Run the container's service with **docker-compose up deployinter** command.

Once the server is running user have to run testcontrol interactive container and then user can run the vsperf client.


===============
testcontrol
===============
For testcontrol also user have two choices auto and interactive.

1. auto
^^^^^^^^^^^^^^^^^^^^^
This auto testcontrol container will perform test automatically on DUT-Host. This container also performing sanity checks automatically. User will also able to get test-status for all tests. If all sanity check doesn't satisfy then test will not run and container gracefully stopped. User can modify the vsperf.conf file which will be upload on DUT-Host automatically by container and used for performing the vsperf test.

Pre-Deployment Configuration
******************
1.User have to provide all the DUT-Host credentials and IP address of TGen-host in list.env. 
2.Provide name for VSPERF_TESTS and VSPERF_CONFFILE in list.env. 
3.Provide option for VSPERF_TRAFFICGEN_MODE and CLEAN_UP [YES or NO] in list.env file.

Build
******************
Run **docker-compose build** command to build the container.

Run
******************
Run the container's service with **docker-compose run testcontrol** command.

User can observe the results and perform the another test by just changing the VSPERF_TEST environment variable in list.env file. 


2. interactive
^^^^^^^^^^^^^^^^^^^^^
This interactive testcontrol container must run before using the vsperf client. It will just run the container and start the server for the vsperf client. This testcontrol interactive container handle all the test related commands from vsperf client and do the operations. Testcontrol interactive container running server on localhost port 50052.

Build
******************
Run **docker-compose build** command to build the container.

Run
******************
Run the container's service with **docker-compose up testcontrolinter** command.

After running this container user can use the vsperf client.