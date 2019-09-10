VSPERF Client
--------------
VSPERF client is a simple python application, which can be used to work with interactive deploy and testcontrol containers.

============
Description
============

VSPERF client is used for both set-up of DUT-Host and TGen-Host as well as run the multiple tests. User can perform different operations by selecting the available options and their sub-options.

VSPERF client provides following options for User.

* Establish Connections
This option allow user to initialize the connections.             
[0]Connect to DUT Host: It will establish connection with DUT-HOST.      
[1]Connect to Tgen Host: This option will establish connection with TGen-Host.

* Installation
After connection has established, user can perform installation for test environment setup.
[0]Install VSPERF : This option will first check either vsperf is installed on DUT or not. If VSPERF is not installed, then it will perform VSPERF installation process on DUT-Host
[1]Install TGen: This is option will check either t-rex is installed on Tgen or not. If t-rex is already installed then it will also check either is working fine or not. If there is not t-rex installed on Tgen then this option will install t-rex on Tgen-HOST
[2]Install Collectd: This is option will install collectd on DUT-Host.

* Upload Configuration Files
Once set-up is done, User can upload configuration files.
[0]Upload TGen Configuration File: It will upload trex_cfg.yaml configuration file on Tgen.[User can either specify path in vsperfclient.conf or externally provide path for the trex_cfg.yaml]
[1]Upload Collectd Configuration File: This is option is use to uplaod collectd configuration file.

* Manage DUT-System Configuration
[0]DUT-Host hugepages configuration: This option allow User to manage hugepages of DUT-Host. [User need to provide value for HpMax and HpRequested in vsperfclient.conf]
[1]Check VSPERF dependencies: Using this option user can check library dependencies on DUT-Host.

* Run Test
[0]Upload Test Configuration File : This option will upload the vsperf test configuration file.
[1]Perform Sanity Checks before running tests : This option has certain sub-options , user must perform all sanity checks before running test. User does not able to start the Vsperf test until all sanity checks satisfied. This sanity check option contains following sub-options like to check VSPERF installed correctly, check Test Config's VNF path is available on DUT-Host, check NIC PCIs is available on Traffic Generator, check installed Collectd, connection between DUT-Host and Traffic Generator Host, check CPU-allocation on DUT-host.
[2]Check if DUT-HOST is available : User can check if DUT-Host is available for Test or not. If DUT-Host available for performing Vsperf user can go ahead and start performing test.
[3]Start TGen : This option will start t-rex traffic generator for test.
[4]Start Beats : This option will start beats on DUT-Host
[5]Start Test : If all the sanity check have performed and traffic generator is running then and then this option will start the vsperf test. Whatever test is defined in vsperfclient.conf will perform using this option. User can also perform multiple tests.

* Test Status
[0]Test status : Using this option, After running test user can check whether their test completed successfully or failed. If user is running multiple test then they can identify the failed test name using this option.
[1]Get Test Configuration file from DUT-host: User can also able to read the test configuration file content they uploaded.

* Clean-Up
[0]Remove VSPERF: This option will completely remove the vsperfenv on DUT-Host
[1]Terminate VSPERF: This option will keep vsperfenv on DUT-Host. If there is any process still running related with the vsperf then this option will terminate all those processes like ovs-vswitchd,ovsdb-server,vppctl,stress,qemu-system-x86_64.
[2]Remove Results from DUT-Host : This is option will remove all the test results located in /tmp folder.
[3]Remove Uploaded Configuration Files: This option will remove all uploaded test configuration file
[4]Remove Collectd: This option will uninstall collectd from the DUT-Host
[5]Remove Everything: This option will execute all the options listed above.

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
