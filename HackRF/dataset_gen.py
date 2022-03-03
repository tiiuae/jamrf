#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Dataset Generator using Hackrf
# Author: Abubakar Sani Ali
# GNU Radio version: 3.8.1.0

###################################################################################
# Importing Libraries
###################################################################################
import math
import os
import time
import yaml
from gnuradio import gr
from gnuradio import blocks
from gnuradio import analog
from gnuradio import digital
from gnuradio import audio
from gnuradio import fft
from gnuradio.fft import window
from gnuradio import filter
from gnuradio.filter import firdes
from statistics import mean
import osmosdr
import sys
import numpy as np
from random import randint


class HackRF:
    """docstring for ."""

    def __init__(self):
        self.samp_rate = 20e6
        self.sdr_bandwidth = 20e6


class Sensor(HackRF):
    """docstring for ."""

    def __init__(self, dataset):
        super(Sensor, self).__init__()
        self.t_sensing = 5
        self.dataset = dataset

    def sense(self, freq):
        tb = gr.top_block()

        osmosdr_source = osmosdr.source(
            args="numchan=" + str(1) + " " + ""
        )
        osmosdr_source.set_time_unknown_pps(osmosdr.time_spec_t())
        osmosdr_source.set_sample_rate(self.samp_rate)
        osmosdr_source.set_center_freq(freq, 0)
        osmosdr_source.set_freq_corr(0, 0)
        osmosdr_source.set_gain(0, 0)
        osmosdr_source.set_if_gain(16, 0)
        osmosdr_source.set_bb_gain(16, 0)
        osmosdr_source.set_antenna('', 0)
        osmosdr_source.set_bandwidth(self.sdr_bandwidth, 0)

        throttle = blocks.throttle(gr.sizeof_gr_complex * 1, self.samp_rate, True)

        low_pass_filter = filter.fir_filter_ccf(
            1,
            firdes.low_pass(
                1,
                self.samp_rate,
                75e3,
                25e3,
                firdes.WIN_HAMMING,
                6.76))

        file_sink = blocks.file_sink(gr.sizeof_gr_complex * 1, self.dataset, False)
        file_sink.set_unbuffered(True)

        tb.connect(osmosdr_source, throttle)
        tb.connect(throttle, low_pass_filter)
        tb.connect(low_pass_filter, file_sink)

        tb.start()
        time.sleep(self.t_sensing)
        tb.stop()
        tb.wait()


def main():
    freq = 2462 * 10e5
    cond = 'idle'
    dataset = f'{cond}_IQ_data.bin'
    if not os.path.isfile(dataset):
        my_sensor = Sensor(dataset)
        my_sensor.sense(freq)
    else:
        print("Dataset already generated")


if __name__ == '__main__':
    main()
