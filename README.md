# opencv-python-window-module
In-progress re-factoring previous efforts in my exploration of OpenCV. The core creates an overlay on the screen for actions / requests. A service class exists that captures the screen and provides the current frame and previous frame. An in memory x, y map is created in relation to the entire screen/viewport. Models can be loaded in. Bounding boxes are generated and applied to the screen/viewport map.

More to come as requirements are built discovered.

## System Requirements
$ sudo apt-get update
$ sudo apt-get install python3.6
$ sudo apt install xdotool
$ sudo apt install python3-xlib
$ sudo apt install libgirepository1.0-dev libcairo2-dev python3-gi python3-gi-cairo
$ sudo apt-get install python3-tk python3-dev
$ sudo apt install gnome-screenshot

## Getting Started
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ python app.py
