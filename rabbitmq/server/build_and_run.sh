#!/bin/bash
sudo docker run -d --hostname host-rabbit --name rabbit --network="host" rabbitmq:3