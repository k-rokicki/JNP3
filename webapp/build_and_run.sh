#!/bin/bash
sudo docker build -t webapp1 .

sudo docker run --name webapp1 --network="host" webapp1
