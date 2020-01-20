#!/bin/bash
sudo docker build -t rabbit-worker .

sudo docker run --name rabbit-worker --network="host" rabbit-worker
