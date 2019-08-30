Vsperf client allow users to perform VSPERF Set-up and VSPERF Test.

User must need to install grpcio, grpcio-tools and configparser for python3 environment.
User can run the Vsperf client script with python3.

For Uploading the configuration files user have two choices

1. User can provide path in vsperfclient.conf file.

2. When running client ask for path use specific path where configuration file exist.

T-rex and collectd configuration file should be saved with trex_cfg.yaml and collectd.conf respectively.
Test configuration file can be saved according to your preferences and reliability.

In order to use Vsperf client, user must have to start servers which can be achieved by running deployment/interactive container and testcontrol/interactive container.


