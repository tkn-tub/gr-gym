#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Simple benchmark
# GNU Radio version: 3.8.2.0

from gnuradio import analog
from gnuradio import blocks
from gnuradio import gr
from gnuradio.filter import firdes
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import zeromq
try:
    from xmlrpc.server import SimpleXMLRPCServer
except ImportError:
    from SimpleXMLRPCServer import SimpleXMLRPCServer
import threading


class simple_benchmark(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Simple benchmark")

        ##################################################
        # Variables
        ##################################################
        self.interval = interval = 1000
        self.action = action = 0

        ##################################################
        # Blocks
        ##################################################
        self.zeromq_pub_sink_0_0 = zeromq.pub_sink(gr.sizeof_int, 1, 'tcp://127.0.0.1:8001', 100, False, -1)
        self.xmlrpc_server_0 = SimpleXMLRPCServer(('localhost', 8080), allow_none=True)
        self.xmlrpc_server_0.register_instance(self)
        self.xmlrpc_server_0_thread = threading.Thread(target=self.xmlrpc_server_0.serve_forever)
        self.xmlrpc_server_0_thread.daemon = True
        self.xmlrpc_server_0_thread.start()
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_int*1, interval,True)
        self.analog_const_source_x_0 = analog.sig_source_i(0, analog.GR_CONST_WAVE, 0, 0, action)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_const_source_x_0, 0), (self.blocks_throttle_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.zeromq_pub_sink_0_0, 0))


    def get_interval(self):
        return self.interval

    def set_interval(self, interval):
        self.interval = interval
        self.blocks_throttle_0.set_sample_rate(self.interval)

    def get_action(self):
        return self.action

    def set_action(self, action):
        self.action = action
        self.analog_const_source_x_0.set_offset(self.action)





def main(top_block_cls=simple_benchmark, options=None):
    if gr.enable_realtime_scheduling() != gr.RT_OK:
        print("Error: failed to enable real-time scheduling.")
    tb = top_block_cls()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()

    try:
        input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
