#!/bin/bash

mkdir -p lnd
mkdir -p ./lnd/lnd
mkdir -p ./lnd/shared
mkdir -p mysql

touch ./subscriber/updates.log

sudo docker-compose down
sudo docker-compose up -d --build
