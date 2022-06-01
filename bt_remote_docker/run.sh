#!/bin/bash
sudo docker run -it --name bluetooth_remote_dev --privileged -t -d \
-v /home/dev/py/bt_remote:/config \
-v /dev/input:/input \
tjntomas/bt_remote:1.0.1
