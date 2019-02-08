This folder contains the source for VSPERF command and control container.
To build a new container, use the Dockerfile.
```sh
docker build . -t vsperfc:latest
```
Command to run the container:
```sh
docker run -d -p 50051:50051 -v /tmp:/usr/src/app vsperf/vsperfc:latest
```
