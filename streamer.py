#!/usr/bin/env python

import tornado.ioloop
import tornado.web
from tornado.options import define, options
import shlex, subprocess, sys

import constants

define("port", default=constants.default_port, help="run on the given port",
       type=int)
define("camera_ip", help="IP address of device serving camera stream", type=str)
define("camera_port", default=constants.default_camera_port, 
       help="Port of device serving camera stream", type=str)

class FishcamHandler(tornado.web.RequestHandler):
    def get(self):
        server_url = "{}://{}".format(self.request.protocol, self.request.host)
        self.write(constants.video_page.format(url=server_url))

class VideoStreamHandler(tornado.web.RequestHandler):
    _chunk_size = 65536

    def initialize(self, mux_command, video_format):
        self.video_format = video_format
        self.mux_command = mux_command.format(server=options.camera_ip,
                                              port=options.camera_port)

    @tornado.web.asynchronous
    def get(self):
        self.set_header("Content-Type", "video/{video_format}".format(
                                              video_format=self.video_format))

        self.muxer_process = subprocess.Popen(shlex.split(self.mux_command),
                                              stderr=subprocess.PIPE,
                                              bufsize=-1, close_fds=True)

        stream_fd = self.muxer_process.stderr.fileno()

        self.stream = tornado.iostream.PipeIOStream(stream_fd)
        self.stream.read_bytes(VideoStreamHandler._chunk_size,
                               self.video_chunk)
        self.flush()

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
        self.finish()

def parse_cli_options():
    options.parse_command_line()
    if options.camera_ip is None:
        sys.stderr.write("ERROR: camera_ip is required\n\n")
        options.print_help()
        sys.exit(1)

application = tornado.web.Application([
    (r"/fishcam.html", FishcamHandler),
    (r"/stream.mp4", VideoStreamHandler, dict(
                              mux_command=constants.mp4_mux_command,
                              video_format="mp4")
    ),
    (r"/stream.webm", VideoStreamHandler, dict(
                              mux_command=constants.webm_mux_command,
                              video_format="webm")
    ),
])

if __name__ == "__main__":
    parse_cli_options()
    application.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
