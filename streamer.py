#!/usr/bin/env python

import tornado.ioloop
import tornado.web
from tornado.options import define, options
import subprocess
import shlex

import constants

define("port", default=constants.default_port, help="run on the given port",
       type=int)

class FishcamHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(constants.video_page.format(url=constants.stream_server_url))

class VideoStreamHandler(tornado.web.RequestHandler):
    _chunk_size = 65536

    def initialize(self, mux_command, rtp_server, rtp_port, video_format):
        self.video_format = video_format
        self.rtp_server = rtp_server
        self.rtp_port = rtp_port
        self.mux_command = mux_command.format(server=rtp_server, port=rtp_port)

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

application = tornado.web.Application([
    (r"/fishcam.html", FishcamHandler),
    (r"/stream.mp4", VideoStreamHandler, dict(
                              mux_command=constants.mp4_mux_command,
                              rtp_server=constants.rtp_server,
                              rtp_port=constants.rtp_port,
                              video_format="mp4")
    ),
    (r"/stream.webm", VideoStreamHandler, dict(
                              mux_command=constants.webm_mux_command,
                              rtp_server=constants.rtp_server,
                              rtp_port=constants.rtp_port,
                              video_format="webm")
    ),
])

if __name__ == "__main__":
    tornado.options.parse_command_line()
    application.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
