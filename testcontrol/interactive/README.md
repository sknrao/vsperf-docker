This folder contains the source for VSPERF command and control container.
To build a new container, use the Dockerfile.
```sh
docker build . -t vsperftest:latest
```
Command to run the container:
```sh
docker run -d -p 4000:4000 -v /tmp:/usr/src/app vsperfctest:latest
```
