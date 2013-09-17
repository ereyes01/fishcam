#!/bin/bash

# read an RTP H.264 stream from the camera device, encode into a 
# video/mp4 stream
gst-launch -v tcpclientsrc host=192.168.1.113 port=4000 protocol=1 ! 'application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264' ! rtph264depay ! queue ! h264parse ! queue ! mp4mux streamable=true fragment-duration=1 presentation-time=true ! queue ! tcpserversink port=9091 sync=false

# I previously had fragment-duration=10 but the first 10 seconds of the stream
# had lots of junk in the image.  The stream seems to look much cleaner at the
# beginning, but still has occasional noise...
