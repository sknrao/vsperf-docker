This repository is to explore the containerization of OPNFV-VSPERF.
Once there is an agreement, this will get merged with original vsperf repo.

This containerized vsperf designed to handle vsperf-setup automatically on DUT.

User have to provide all the DUT-Host and Traffic generator related credentials in list.env.

Required commands:

1. Build the docker-compose file

docker-compose build

2. Run both the individual services.

docker-compose run controller

User can analyze the outputs of docker-compose run and manage the further configurations.
Everything looks good then user can run the testcontrol auto container and perform vsperf test.


