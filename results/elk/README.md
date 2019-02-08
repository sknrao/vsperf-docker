### Please set the limit on mmap counts equal to 262144 or more.

There are two options. Run this command:
```sh

sysctl -w vm.max_map_count = 262144

```
or, to set it permanently, update the
```sh

vm.max_map_count

```
setting in

```sh

/etc/sysctl.conf

```

### Update the IP address.
You may want to modify the IP address from 0.0.0.0 to appropriate host-ip in
```sh
docker-compose.yml

```

### Changes made to sebp/elk
The vsperf/elk image is same as sebp/elk with a minor change - the inclusion of collectd codec to logstash.
In the Dockerfile of sebp/elk, under logstash configuration, following lines are added:
```sh
 WORKDIR ${LOGSTASH_HOME}
 RUN gosu logstash bin/logstash-plugin install logstash-codec-collectd
 WORKDIR /

```
