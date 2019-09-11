This repository is to explore the containerization of OPNFV-VSPERF.
Once there is an agreement, this will get merged with original vsperf repo.

This container used to start the server for the vsperf client which will handle all Vsperf Test related operations.

Required commands:

1. Build the docker-compose file

docker-compose build

2. Run the individual service which will start server for vsperf client.

docker-compose up testcontrol


 


