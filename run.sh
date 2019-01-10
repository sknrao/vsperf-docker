#!/bin/sh
docker run -d -p 50051:50051 -v /home/sridhar:/usr/src/app vsperf/vsperfc:latest
