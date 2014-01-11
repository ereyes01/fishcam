#!/usr/bin/env python

default_port = 9090

# TODO: These are hardcoded right now, but they need to be computed
# dynamically.  Sessions need to be defined for logged in users, and
# their camera must be located... this aspect needs a little more 
# design still
rtp_server = "192.168.1.143"
rtp_port = 4000
stream_server_url = "http://eddy.knowsitall.info:9090"

mp4_mux_command = "gst-launch -q "                                          \
    "tcpclientsrc host={server} port={port} protocol=1 ! "                  \
    "'application/x-rtp, media=(string)video, clock-rate=(int)90000, "      \
        "encoding-name=(string)H264' ! "                                    \
    "rtph264depay ! queue ! "                                               \
    "h264parse ! queue ! "                                                  \
    "mp4mux streamable=true fragment-duration=5 presentation-time=true ! "  \
        "queue ! "                                                          \
    "filesink location=/dev/stderr"

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

video_page = """
<!DOCTYPE html> <html> <body>

<video controls autoplay>
<source src="{url}/stream.mp4" autoplay type="video/mp4">
</video>

</body> </html>
"""

if __name__ == "__main__":
    pass
