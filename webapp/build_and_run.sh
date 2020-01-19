#!/bin/bash
sudo docker build -t webapp .

sudo docker run --name webapp --network="host" webapp
