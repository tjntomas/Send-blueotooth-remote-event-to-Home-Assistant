# Catch bluetooth remote event keycodes on a Linux machine and send to Home Assistant as events to use in automations etc.

This repo contains files to build a docker container that will monitor input devices connected to a linux machine, for instance bluetooth remote controls, but any input device can be monitored. The resulting keypress codes will be sent to your Home Assistant instance.

This assumes that you know how docker containers are built and run and that you have already paired your bluetooth remote with the linux machine so I'm not including any instructions for pairing or for using the docker commands.



# 1. Find the input device to use

First, download the `bt_remote_docker` folder in this repo and ssh to the `bt_remote_docker/code` directory.
Make sure you have pip installed required modules in the `/code/reqs.txt`file. They are only needed to run the `find_devices.py` script.
Run `sudo python3 find_devices.py`. Sudo is needed to access the /dev/ devices.
This will list the device names and the device paths for all input devices on your machine. Example output from an Ubuntu machine:

* Telink Trust Keyboard & Mouse event8
* Telink Trust Keyboard & Mouse System Control event7
* Telink Trust Keyboard & Mouse Consumer Control event6
* Telink Trust Keyboard & Mouse event5
* HDA Intel PCH HDMI/DP,pcm=10 event18
* HDA Intel PCH HDMI/DP,pcm=9 event17
* HDA Intel PCH HDMI/DP,pcm=8 event16
* HDA Intel PCH HDMI/DP,pcm=7 event15
* HDA Intel PCH HDMI/DP,pcm=3 event14
* HDA Intel PCH Headphone event13
* HDA Intel PCH Mic event12
* DP-2 event11
* Video Bus event10
* ITE8708 CIR transceiver event9
* SG.Ltd SG Control Mic event4
* SG.Ltd SG Control Mic Keyboard event3
* Power Button event2
* Power Button event1
* Sleep Button event0

In my case, the remote control I want is named
`SG.Ltd SG Control Mic Keyboard` located in the path `/dev/input/event3`

# 2 Edit the `config.yaml` file
Copy the name to the devices list in the `/bt_remote_docker/config.yaml` file and edit all other relevant entries in the config file.

# 3 Build and run the docker container
Make sure the build.sh and run.sh scripts are executable by `sudo chmod +x build.sh && sudo chmod +x run.sh`
Now build the container with `./build.sh`

# 4 Edit the path to your config.yaml file
Edit the `run.sh` file and change the line
`-v /home/dev/py/bt_remote:/config \` 
change `/home/dev/py/bt_remote` to the local path where you store the config.yaml file. 

# 5 Run the container
Now run the container with `./run.sh`

# 6 View the event in Home Asssistant
Open developers tools in HA and go to events.
In the "event to subscribe to" field, enter the `event_name`from your edited `config.yaml` file, default is `mi_bt_remote`, and press the "Start listening" button. You should no see the incoming events when a remote button is pressed.

