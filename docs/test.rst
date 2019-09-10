Before using VSPERF client and VSPERF containers user must run the prepare.sh script which will prepare their local environment.

locate vsperf-docker/prepare.sh and run:
bash prepare.sh

VSPERF Containers
------------------

============
deployment
============
User have two choices for deployment, auto and interactive.

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
For testcontrol also user have two choices , auto and interactive.

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
