#!/bin/bash
sudo docker build -t varnish .

sudo docker run --name varnish --network="host" varnish
