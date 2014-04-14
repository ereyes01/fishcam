#!/usr/bin/env python

default_port = 9090

# TODO: The camera device should connect as a client, which should 
# obviate the need to hardcode IP addresses here. This app should run a
# gstreamer server that can service multiple HTTP clients. Not sure if 
# it makes sense to support >1 camera device per instance of this
# application, might be interesting if the need arises.
rtp_server = "192.168.1.143"
rtp_port = 4000
stream_server_url = "http://eddy.knowsitall.info:9090"

mp4_mux_command = "gst-launch -q "                                          \
    "tcpclientsrc host={server} port={port} protocol=1 ! "                  \
    "'application/x-rtp, media=(string)video, clock-rate=(int)90000, "      \
        "encoding-name=(string)H264' ! "                                    \
    "rtph264depay ! queue ! "                                               \
    "h264parse ! queue ! "                                                  \
    "mp4mux streamable=true fragment-duration=5 ! "                         \
        "queue ! "                                                          \
    "filesink location=/dev/stderr"

# This causes the server to transcode to VP8. It's super slow on 1 CPU!
# Is there any way to parallelize this?
webm_mux_command = "gst-launch -q "                                         \
    "tcpclientsrc host={server} port={port} protocol=1 ! "                  \
    "'application/x-rtp, media=(string)video, clock-rate=(int)90000, "      \
        "encoding-name=(string)H264' ! "                                    \
        "rtph264depay ! queue ! "                                           \
        "ffdec_h264 ! queue ! "                                             \
        "ffmpegcolorspace ! queue ! "                                       \
        "vp8enc ! queue ! "                                                 \
        "webmmux streamable=true ! queue ! "                                \
        "filesink  location=/dev/stderr"

# Right now only serving embedded H.264 video. WebM/VP8 is too slow (see
# comment above).
video_page = """
<!DOCTYPE html> <html> <body>

<video controls autoplay>
<source src="{url}/stream.mp4" autoplay type="video/mp4">
</video>

</body> </html>
"""

if __name__ == "__main__":
    pass
