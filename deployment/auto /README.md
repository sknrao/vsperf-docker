This repository is to explore the containerization of OPNFV-VSPERF.
Once there is an agreement, this will get merged with original vsperf repo.

This containerized vsperf designed to handle vsperf-setup automatically on DUT.

User have to provide all the DUT-Host and Traffic genretor related User_name and password on list.env.

Required commands:

1. run the docker-compose file

sudo docker-compose build

2. Run both the individual services.

sudo docker-compose run controller

Now, User can analyze the outputs of docker-compose run and manage the further configurations.

