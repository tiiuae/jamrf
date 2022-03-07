#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
# Author: Abubakar Sani Ali
# GNU Radio version: 3.8.1.0

###################################################################################
# Importing Libraries
###################################################################################

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


class Jammer(HackRF):
    """
    Jammer class is a parent class for all jammer types
    """

    def __init__(self, waveform, power, t_jamming):
        super(Jammer, self).__init__()
        self.RF_gain = None
        self.IF_gain = None
        self.waveform = waveform
        self.power = power
        self.t_jamming = t_jamming
        self.qpsk_const = digital.constellation_rect([-1 - 1j, -1 + 1j, 1 + 1j, 1 - 1j], [0, 1, 3, 2],
                                                     4, 2, 2, 1, 1).base()

    def set_gains(self):
        if -40 <= self.power <= 5:
            self.RF_gain = 0
            if self.power < -5:
                self.IF_gain = self.power + 40
            elif -5 <= self.power <= 2:
                self.IF_gain = self.power + 41
            elif 2 < self.power <= 5:
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

        if self.waveform == 1:
            source = analog.sig_source_c(self.samp_rate, analog.GR_SIN_WAVE, 1000, 1, 0, 0)
        elif self.waveform == 2:
            source = blocks.vector_source_b(list(map(int, np.random.randint(0, 255, 1000))), True)
        elif self.waveform == 3:
            source = analog.noise_source_c(analog.GR_GAUSSIAN, 1, 0.5)
        else:
            print("invalid selection")

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
        throttle = blocks.throttle(gr.sizeof_gr_complex * 1, self.samp_rate, True)
        digital_constellation_modulator = digital.generic_mod(
            constellation=self.qpsk_const,
            differential=True,
            samples_per_symbol=4,
            pre_diff_code=True,
            excess_bw=0.035,
            verbose=False,
            log=False)

        if self.waveform == 2:
            tb.connect(source, digital_constellation_modulator)
            tb.connect(digital_constellation_modulator, throttle, osmosdr_sink)
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
        super(Sensor, self).__init__()
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
        complex_to_mag_squared = blocks.complex_to_mag_squared(1)

        file_sink = blocks.file_sink(gr.sizeof_float * 1, 'output.bin', False)
        file_sink.set_unbuffered(True)

        tb.connect(osmosdr_source, throttle)
        tb.connect(throttle, low_pass_filter)
        tb.connect(low_pass_filter, complex_to_mag_squared)
        tb.connect(complex_to_mag_squared, file_sink)

        tb.start()
        time.sleep(self.t_sensing)
        tb.stop()
        tb.wait()


def set_frequency(init_freq, channel, ch_dist):
    if channel == 1:
        freq = init_freq
    else:
        freq = init_freq + (channel - 1) * ch_dist
    return freq


def detect(options, my_sensor):
    ch_activity_flag = 0
    if options.get("detector") == 1:
        with open("output.bin", mode='rb') as file:
            fileContent = file.read()
            samples = np.memmap("output.bin", mode="r", dtype=np.float32)

        energy = 0.5 * mean(samples)
        if energy > my_sensor.threshold:
            ch_activity_flag = 1
    elif options.get("detector") == 2:
        # implement machine learning based detector here
        pass
    else:
        pass

    return ch_activity_flag


def jamming(my_jammer, freq, options):
    flag = 0
    if options.get("jamming") == 1:
        print(f'\nThe frequency to jam is: {freq/10e5}MHz')
        my_jammer.jam(freq)
    elif options.get("jamming") == 2:
        print(f'\nThe frequency to sense is: {freq/10e5}MHz')
        my_sensor = Sensor()
        my_sensor.sense(freq)
        ch_active = detect(options, my_sensor)
        if ch_active == 1:
            print(f'\nSensed activity will jam: {freq/10e5}MHz')
            my_jammer.jam(freq)
            if options.get("memory") == 1:
                flag = 1
    else:
        pass
    return flag


def constant(options):
    t_j, t_s = enable_energy_savings(options.get("t_jamming"), options.get("memory"))
    my_jammer = Jammer(options.get("waveform"), options.get("power"), t_j)
    freq = options.get("freq") * 10e5
    jamming(my_jammer, freq, options)
    time.sleep(t_s)


def sweeping(init_freq, lst_freq, options):
    channel = 1
    n_channels = (lst_freq - init_freq) // (options.get("ch_dist")*10e5)
    t_j, t_s = enable_energy_savings(options.get("t_jamming"), options)
    start_time = time.time()
    while True:
        my_jammer = Jammer(options.get("waveform"), options.get("power"), t_j)
        freq = set_frequency(init_freq, channel, options.get("ch_dist")*10e5)
        m_flag = jamming(my_jammer, freq, options)
        time.sleep(t_s)
        if m_flag == 0:
            channel = 1 if channel > n_channels else channel + 1
        else:
            pass
        jamming_time_per_run = time.time() - start_time
        if jamming_time_per_run >= options.get("duration"):
            break


def hopping(init_freq, lst_freq, options):
    n_channels = (lst_freq - init_freq) // (options.get("ch_dist")*10e5)
    channel = randint(1, n_channels + 1)
    t_j, t_s = enable_energy_savings(options.get("t_jamming"), options)
    start_time = time.time()
    while True:
        my_jammer = Jammer(options.get("waveform"), options.get("power"), t_j)
        freq = set_frequency(init_freq, channel, options.get("ch_dist")*10e5)
        m_flag = jamming(my_jammer, freq, options)
        time.sleep(t_s)
        if m_flag == 0:
            channel = randint(1, n_channels + 1)
        jamming_time_per_run = time.time() - start_time
        if jamming_time_per_run >= options.get("duration"):
            break


def enable_energy_savings(t_jamming, options):
    savings = options.get("savings")
    if savings == 1:
        duty_cycle = options.get("duty_cycle")
        t_j = t_jamming * duty_cycle / 100
        t_s = t_jamming - t_j
    else:
        t_j = t_jamming
        t_s = 0
    return t_j, t_s
