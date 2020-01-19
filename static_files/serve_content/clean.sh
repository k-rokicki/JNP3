#!/bin/bash
sudo docker image rm serve_static_content --force
sudo docker container rm serve_static_content --force
