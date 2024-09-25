#!/bin/bash

sudo docker run -d \
        --name mnist-mariadb \
	-e MARIADB_USER=mnist \
	-e MARIADB_PASSWORD=1234 \
	-e MARIADB_DATABASE=mnistdb \
	-e MARIADB_ROOT_PASSWORD=my-secret-pw \
	-p 53306:3306 \
	mariadb:latest
