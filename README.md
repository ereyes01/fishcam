# Raspberry Pi c920 Fishcam

This program serves a live video feed into my home aquarium over a web service.

The video itself comes from a Raspberry Pi with an attached webcam. The
video feed is already encoded in H.264 and arrives via an RTP/TCP 
stream created by GStreamer on the Raspberry Pi.

Currently, the Raspberry Pi is the server of the stream. You must point the 
web service at it via a command line argument.

To obtain the code, run the following command:

```
$ git clone https://github.com/ereyes01/fishcam.git
```

## HTTP Stream Server

Make sure you have the following dependencies installed:

```
$ sudo apt-get install gstreamer-tools gstreamer0.10-ffmpeg gstreamer0.10-gconf gstreamer0.10-plugins-bad gstreamer0.10-plugins-base gstreamer0.10-plugins-good gstreamer0.10-plugins-ugly
```

```
$ pip install tornado
```

For the Python stuff, it is strongly recommended that you use a [virtualenv](http://www.virtualenv.org/en/latest/).

Take note of your camera / Raspberry Pi's IP address.

You can execute the server by running:

```
$ python streamer.py --camera_ip=192.168.0.5
```

Replace the IP above with your Raspberry Pi's IP address. The service's logs 
will appear on stdout.

You can also read about all the available options by printing the help message:

```
$ python streamer.py --help
```

## Raspberry Pi

The raspberry-pi subdirectory contains the code that runs on the
Raspberry Pi. It isn't much as you can see. The main files are:

- capture.c:
Reads H.264 bits from the Logitech c920. This code is a slightly 
tweaked version of the one from [csete's bonecam](https://github.com/csete/bonecam)

- video-server
This script initializes the camera and creates a video stream out of
the video feed collected by the capture program. This is also derived from
[csete's bonecam](https://github.com/csete/bonecam).

Ideally, this should be packaged into a deb or something. That is a future
work item.

Follow these steps to deploy this program onto your Raspberry Pi (my system is 
running Raspbian):

Copy the code onto your Raspberry Pi:

```
$ tar -cf - ./raspberry-pi | ssh pi@192.168.0.5 "tar -xvf - && mv raspberry-pi webcam"
```

Replace the IP above with your Raspberry Pi's IP address.

V4l / Gstreamer Dependencies:

```
$ sudo apt-get install libv4l-dev v4l-utils gstreamer-tools gstreamer0.10-ffmpeg gstreamer0.10-gconf gstreamer0.10-plugins-bad gstreamer0.10-plugins-base gstreamer0.10-plugins-good gstreamer0.10-plugins-ugly
```

The capture.c program must be built with an ARM C compiler. Since it is
so small of a program, the simplest way to build it would be on the 
Raspberry Pi itself.  Installing gcc is simple:

```
$ sudo apt-get install gcc
```

... then to compile a binary for capture.c:

```
$ cd ~/webcam
```

```
$ gcc -O2 -Wall `pkg-config --cflags --libs libv4l2` capture.c -o capture
```

To start the video feed from the Raspberry Pi, run the following commands:

```
$ cd ~/webcam
```

```
$ ./video-server 0.0.0.0 4000
```

That will start a server that the web service can connect to. The LED on the 
camera should light up blue if this is working. This server needs to be running
on the Raspberry Pi in order for the web service to work.

Now, with your Tornado server and your Raspberry Pi streaming video, you can
watch your video feed on the browser by visiting: 

http://localhost:9090/fishcam.html

Hope these instructions help you get up and running!

Please open an issue if you're having trouble, or if you've found that I broke 
something.
