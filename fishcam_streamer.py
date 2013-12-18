#!/usr/bin/python

import tornado.ioloop
import tornado.web
from tornado.options import define, options
import subprocess
import shlex

define("port", default=9090, help="run on the given port", type=int)

# TODO: These are hardcoded right now, but they need to be computed
# dynamically.  Sessions need to be defined for logged in users, and
# their camera must be located... this aspect needs a little more 
# design still
rtp_server = "192.168.1.113"
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

class FishcamHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("""
        <!DOCTYPE html> <html> <body>

        <video controls autoplay>
        <source src="{url}/stream.mp4" autoplay type="video/mp4">
        </video>

        </body> </html>
        """.format(url=stream_server_url))

class VideoStreamHandler(tornado.web.RequestHandler):
    _chunk_size = 4096

    @tornado.web.asynchronous
    def get(self):
        self.set_header("Content-Type", "video/mp4")

        formatted_command = mp4_mux_command.format(
                                server  = rtp_server, 
                                port    = rtp_port)

        self.muxer_process = subprocess.Popen(shlex.split(formatted_command),
                                              stderr=subprocess.PIPE,
                                              bufsize=-1, close_fds=True)

        stream_fd = self.muxer_process.stderr.fileno()

        self.stream = tornado.iostream.PipeIOStream(stream_fd)
        self.stream.read_bytes(VideoStreamHandler._chunk_size,
                               self.video_chunk)

    def video_chunk(self, data):
        self.write(data)
        self.flush()
        self.stream.read_bytes(VideoStreamHandler._chunk_size,
                               self.video_chunk)

    def cleanup_muxer(self):
        self.muxer_process.terminate()
        self.muxer_process.wait()

    def on_connection_close(self):
        self.stream.close()
        self.cleanup_muxer()

application = tornado.web.Application([
    (r"/fishcam.html", FishcamHandler),
    (r"/stream.mp4", VideoStreamHandler),
])

if __name__ == "__main__":
    tornado.options.parse_command_line()
    application.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
