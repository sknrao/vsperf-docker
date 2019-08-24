This repository is to explore the containerization of OPNFV-VSPERF.
Once there is an agreement, this will get merged with original vsperf repo.

This containerized vsperf designed to handle vsperf-test automatically on DUT.

User have to provide all the DUT-host related User_name and password on list.env.

Required commands:

1. Build the docker-compose file

docker-compose build

2. Run both the individual services.

docker-compose run testcontrol

Now, User can analyze the outputs of docker-compose run and perform the new test by just editing the list.env "VSPERF_TEST" parameter.

We highly recommend User's to configure CLEAN_UP environment variable very carefully. (Especially when user is running test on Intel-POD 12 , Node-4)

 


