#!/bin/bash

# read an RTP H.264 stream from the camera device, encode into a 
# video/mp4 stream
gst-launch -v tcpclientsrc host=192.168.1.113 port=4000 protocol=1 ! 'application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264' ! rtph264depay ! queue ! h264parse ! queue ! mp4mux streamable=true fragment-duration=10 presentation-time=true ! queue ! tcpserversink port=9091 sync=false
