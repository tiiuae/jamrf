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

        if self.waveform == 'mod_sine' or self.waveform == '1':
            source = analog.sig_source_c(self.samp_rate, analog.GR_SIN_WAVE, 1000, 1, 0, 0)
        elif self.waveform == 'swept_sine' or self.waveform == '2':
            source = analog.sig_source_f(self.samp_rate, analog.GR_SIN_WAVE, 1000, 1, 0, 0)
        elif self.waveform == 'noise' or self.waveform == '3':
            source = analog.noise_source_c(analog.GR_GAUSSIAN, 1, 0.5)
        else:
            print("invalid selection")

        freq_mod = analog.frequency_modulator_fc(1)
        osmosdr_sink = osmosdr.sink(
            args="numchan=" + str(1) + " " + ""
        )
        osmosdr_sink.set_time_unknown_pps(osmosdr.time_spec_t())
        osmosdr_sink.set_sample_rate(self.samp_rate)
        osmosdr_sink.set_center_freq(freq, 0)
        osmosdr_sink.set_freq_corr(0, 0)
        osmosdr_sink.set_gain(self.RF_gain, 0)
        osmosdr_sink.set_if_gain(self.IF_gain, 0)
        osmosdr_sink.set_bb_gain(20, 0)
        osmosdr_sink.set_antenna('', 0)
        osmosdr_sink.set_bandwidth(self.sdr_bandwidth, 0)
        throttle = blocks.throttle(gr.sizeof_gr_complex*1, self.samp_rate,True)

        if self.waveform == 'swept_sine' or self.waveform == '2':
            tb.connect(source,freq_mod)
            tb.connect(freq_mod, throttle, osmosdr_sink)
        else:
            tb.connect(source, throttle)
            tb.connect(throttle, osmosdr_sink)

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

        throttle = blocks.throttle(gr.sizeof_gr_complex*1, self.samp_rate,True)

        low_pass_filter = filter.fir_filter_ccf(
            1,
            firdes.low_pass(
                1,
                self.samp_rate,
                75e3,
                25e3,
                firdes.WIN_HAMMING,
                6.76))
        complex_to_mag_squared = blocks.complex_to_mag_squared(1)

        file_sink = blocks.file_sink(gr.sizeof_float*1, 'output.bin', False)
        file_sink.set_unbuffered(True)

        tb.connect(osmosdr_source, throttle)
        tb.connect(throttle, low_pass_filter)
        tb.connect(low_pass_filter, complex_to_mag_squared)
        tb.connect(complex_to_mag_squared, file_sink)

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

def jamming(jamming_type, my_Jammer, freq, memory):
    flag = 0
    if jamming_type == 'proactive' or jamming_type == '1':
        my_Jammer.jam(freq)
    elif jamming_type == 'reactive' or jamming_type == '2':
        my_Sensor = Sensor()
        my_Sensor.sense(freq)
        rx_power = my_Sensor.detect()
        if rx_power > my_Sensor.threshold:
            my_Jammer.jam(freq)
            flag = 1 if memory == 'yes' or memory == 'y'
    return flag

def constant(jamming_type, duration, waveform, power, t_jamming, freq):
    my_Jammer = Jammer(waveform, power, t_jamming)
    start_time = time.time()
    jamming(jamming_type, my_Jammer, freq)
    jamming_time_per_exp = time.time() - start_time
    time_rem = duration - jamming_time_per_exp
    if time_rem > 0:
        time.sleep(time_rem)

def sweeping(jamming_type, duration, waveform, power, t_jamming, init_freq, lst_freq, ch_dist):
    channel = 1
    n_channels = (lst_freq - init_freq)//ch_dist
    memory = enable_memory(jamming_type)
    start_time = time.time()
    while True:
        my_Jammer = Jammer(waveform, power, t_jamming)
        freq = my_Jammer.set_frequency(init_freq, channel, ch_dist)
        m_flag = run_jamming(jamming_type, my_Jammer, freq, memory)
        if m_flag == 0:
            channel = 1 if channel > n_channels else channel + 1
        else:
            pass
        jamming_time_per_exp = time.time() - start_time
        if jamming_time_per_exp >= duration:
            break

def hopping(jamming_type, duration, waveform, power, t_jamming, init_freq, lst_freq, ch_dist):
    channel = randint(1, n_channels + 1)
    n_channels = (lst_freq - init_freq)//ch_dist
    memory = enable_memory(jamming_type)
    start_time = time.time()
    while True:
        my_Jammer = Jammer(waveform, power, t_jamming)
        freq = my_Jammer.set_frequency(init_freq, channel, ch_dist)
        m_flag = run_jamming(jamming_type, my_Jammer, freq, memory)
        if m_flag == 0:
            channel = randint(1, n_channels + 1)
        jamming_time_per_exp = time.time() - start_time
        if jamming_time_per_exp >= duration:
            break
            
def enable_memory(jamming_type):
    if jamming_type == 'reactive' or jamming_type == '2':
        memory = input('Enable memory feature (yes|no): ')
    else:
        memory = 'no'
    return memory

def run_jamming(jamming_type, my_Jammer, freq, memory):
    if memory == 'yes' or memory == 'y':
        m_flag = jamming(jamming_type, my_Jammer, freq, memory)
    else:
        m_flag = jamming(jamming_type, my_Jammer, freq)
