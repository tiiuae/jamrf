#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
# Author: abubakar
# GNU Radio version: 3.8.1.0

###################################################################################
# Importing Libraries
###################################################################################

import time
from gnuradio import gr
from gnuradio import blocks
from gnuradio import analog
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

    def set_frequency(self, init_freq, channel, ch_dist):
        if channel == 1:
            freq = init_freq
        else:
            freq = init_freq + (channel - 1) * ch_dist
        return freq

class Jammer(HackRF):
    """
    Jammer class is a parent class for all jammer types
    """

    def __init__(self, waveform, power, t_jamming):
        super(Jammer, self).__init__()
        self.waveform = waveform
        self.power = power
        self.t_jamming = t_jamming

    def set_gains(self):
        if self.power >= -40 and self.power <= 5:
            self.RF_gain = 0
            if self.power < -5:
                self.IF_gain = self.power + 40
            elif self.power >= -5 and self.power <= 2:
                self.IF_gain = self.power + 41
            elif self.power > 2 and self.power <= 5:
                self.IF_gain = self.power + 42
        elif self.power > 5:
            self.RF_gain = 14
            self.IF_gain = self.power + 34
        else:
            print("invalid Jammer Transmit power")

        return self.RF_gain, self.IF_gain

    def jam(self, freq):
        self.RF_gain, self.IF_gain = self.set_gains()

        tb = gr.top_block()

        if self.waveform == 'mod_sine':
            self.source = analog.sig_source_c(self.samp_rate, analog.GR_SIN_WAVE, 1000, 1, 0, 0)
        elif self.waveform == 'swept_sine':
            self.source = analog.sig_source_f(self.samp_rate, analog.GR_SIN_WAVE, 1000, 1, 0, 0)
        elif self.waveform == 'noise':
            self.source = analog.noise_source_c(analog.GR_GAUSSIAN, 1, 0.5)
        else:
            print("invalid selection")

        self.freq_mod = analog.frequency_modulator_fc(1)
        self.osmosdr_sink = osmosdr.sink(
            args="numchan=" + str(1) + " " + ""
        )
        self.osmosdr_sink.set_time_unknown_pps(osmosdr.time_spec_t())
        self.osmosdr_sink.set_sample_rate(self.samp_rate)
        self.osmosdr_sink.set_center_freq(freq, 0)
        self.osmosdr_sink.set_freq_corr(0, 0)
        self.osmosdr_sink.set_gain(self.RF_gain, 0)
        self.osmosdr_sink.set_if_gain(self.IF_gain, 0)
        self.osmosdr_sink.set_bb_gain(20, 0)
        self.osmosdr_sink.set_antenna('', 0)
        self.osmosdr_sink.set_bandwidth(self.sdr_bandwidth, 0)

        if self.waveform == 2:
            tb.connect(self.source, self.freq_mod, self.osmosdr_sink)
        else:
            tb.connect(self.source, self.osmosdr_sink)

        tb.start()
        time.sleep(self.t_jamming)
        tb.stop()
        tb.wait()

class Sensor(HackRF):
    """docstring for ."""

    def __init__(self):
        super(Sensor,self).__init__()
        self.t_sensing = 0.05
        self.threshold = 0.0002

    def sense(self, freq):
        tb = gr.top_block()

        self.osmosdr_source = osmosdr.source(
                args="numchan=" + str(1) + " " + ""
        )
        self.osmosdr_source.set_time_unknown_pps(osmosdr.time_spec_t())
        self.osmosdr_source.set_sample_rate(self.samp_rate)
        self.osmosdr_source.set_center_freq(freq, 0)
        self.osmosdr_source.set_freq_corr(0, 0)
        self.osmosdr_source.set_gain(0, 0)
        self.osmosdr_source.set_if_gain(16, 0)
        self.osmosdr_source.set_bb_gain(16, 0)
        self.osmosdr_source.set_antenna('', 0)
        self.osmosdr_source.set_bandwidth(self.sdr_bandwidth, 0)

        self.low_pass_filter = filter.fir_filter_ccf(
            1,
            firdes.low_pass(
                1,
                self.samp_rate,
                75e3,
                25e3,
                firdes.WIN_HAMMING,
                6.76))
        self.complex_to_mag_squared = blocks.complex_to_mag_squared(1)

        self.file_sink = blocks.file_sink(gr.sizeof_float*1, 'output.bin', False)
        self.file_sink.set_unbuffered(True)

        tb.connect(self.osmosdr_source, self.low_pass_filter)
        tb.connect(self.low_pass_filter, self.complex_to_mag_squared)
        tb.connect(self.complex_to_mag_squared, self.file_sink)

        tb.start()
        time.sleep(self.t_sensing)
        tb.stop()
        tb.wait()

    def detect(self):
        with open("output.bin", mode = 'rb') as file:
            fileContent = file.read()
            samples = np.memmap("output.bin", mode = "r", dtype = np.float32)

        p = 0.5 * mean(samples)
        return p

def jamming(jamming_type, my_Jammer, freq):
    if jamming_type == 'proactive':
        my_Jammer.jam(freq)
    elif jamming_type == 'reactive':
        my_Sensor = Sensor()
        my_Sensor.sense(freq)
        rx_power = my_Sensor.detect()
        if rx_power > my_Sensor.threshold:
            my_Jammer.jam(freq)

def constant(waveform, power, t_jamming, freq):
    my_Jammer = Jammer(waveform, power, t_jamming)
    my_Jammer.jam(freq)

def sweeping(jamming_type, duration, waveform, power, t_jamming, init_freq, lst_freq, ch_dist):
    channel = 1
    n_channels = (lst_freq - init_freq)//ch_dist
    start_time = time.time()
    while True:
        my_Jammer = Jammer(waveform, power, t_jamming)
        freq = my_Jammer.set_frequency(init_freq, channel, ch_dist)
        jamming(jamming_type, my_Jammer, freq)
        channel = 1 if channel > n_channels else channel + 1
        jamming_time_per_exp = time.time() - start_time
        if jamming_time_per_exp > duration:
            break

def hopping(jamming_type, duration, waveform, power, t_jamming, init_freq, lst_freq, ch_dist):
    n_channels = (lst_freq - init_freq)//ch_dist
    start_time = time.time()
    while True:
        channel = randint(1, n_channels + 1)
        my_Jammer = Jammer(waveform, power, t_jamming)
        freq = my_Jammer.set_frequency(init_freq, channel, ch_dist)
        jamming(jamming_type, my_Jammer, freq)
        jamming_time_per_exp = time.time() - start_time
        if jamming_time_per_exp > duration:
            break
