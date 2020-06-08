# DSLR Automatic Time Lapse
This script is created to take a time lapse overnight on a DSLR camera compatible with the gphoto2 library. I am using my Nikon D3200 and a RPi Zero W for the setup.

# Dependencies & Setup
- gphoto2
$ pip install gphoto2
- astral
$ pip install astral
- argparse
$ pip install argparse

Connect RPi (or other device) to the camera using the USB cable.

# Execution
$ python3 DSLR_timelapse.py -h
	-> It shows command line options
Main parameters to control:
- delay between pictures
- start/end time
- offset from start/end time
