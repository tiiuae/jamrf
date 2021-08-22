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

class JamRF():
    """
    JamRF is a class developed to investigate the impact of radio frequency
    jamming using Hackrf sdr. It models two different functions of the sdr i.e
    receiveing(sensing) and transmitting(jamming).
    """

    def __init__(self, jamming, jammer, waveform, power, t_jamming, ch_dist):
        self.jamming = jamming
        self.jammer = jammer
        self.waveform = waveform
        self.power = power
        self.t_jamming = t_jamming
        self.ch_dist = ch_dist
        self.samp_rate = 20e6
        self.sdr_bandwidth = 20e6
        if self.jamming == 2:
            self.t_sensing = 0.05

    def set_frequency(self, init_freq, channel):
        if self.channel == 1:
            self.freq = self.init_freq
        else:
            self.freq = self.init_freq + (self.channel - 1) * self.ch_dist
        return self.freq

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

    def detect(self):
        with open("output.bin", mode = 'rb') as file:
            fileContent = file.read()
            samples = np.memmap("output.bin", mode = "r", dtype = np.float32)

        self.p = 0.5 * mean(samples)
        return self.p

    def sense(self, freq):
        tb = gr.top_block()

        self.osmosdr_source = osmosdr.source(
                args="numchan=" + str(1) + " " + ""
        )
        self.osmosdr_source.set_time_unknown_pps(osmosdr.time_spec_t())
        self.osmosdr_source.set_sample_rate(samp_rate)
        self.osmosdr_source.set_center_freq(freq, 0)
        self.osmosdr_source.set_freq_corr(0, 0)
        self.osmosdr_source.set_gain(0, 0)
        self.osmosdr_source.set_if_gain(16, 0)
        self.osmosdr_source.set_bb_gain(16, 0)
        self.osmosdr_source.set_antenna('', 0)
        self.osmosdr_source.set_bandwidth(sdr_bandwidth, 0)

        self.low_pass_filter = filter.fir_filter_ccf(
            1,
            firdes.low_pass(
                1,
                samp_rate,
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

    def jam(self, freq):
        self.RF_gain, self.IF_gain = self.set_gains()

        tb = gr.top_block()

        if self.waveform == 1:
            self.source = analog.sig_source_c(samp_rate, analog.GR_SIN_WAVE, 1000, 1, 0, 0)
        elif self.waveform == 2:
            self.source = analog.sig_source_f(samp_rate, analog.GR_SIN_WAVE, 1000, 1, 0, 0)
        elif self.waveform == 3:
            self.source = analog.noise_source_c(analog.GR_GAUSSIAN, 1, 0.5)
        else:
            print("invalid selection")

        self.freq_mod = analog.frequency_modulator_fc(1)
        self.osmosdr_sink = osmosdr.sink(
            args="numchan=" + str(1) + " " + ""
        )
        self.osmosdr_sink.set_time_unknown_pps(osmosdr.time_spec_t())
        self.osmosdr_sink.set_sample_rate(self.samp_rate)
        self.osmosdr_sink.set_center_freq(self.freq, 0)
        self.osmosdr_sink.set_freq_corr(0, 0)
        self.osmosdr_sink.set_gain(self.RF_gain, 0)
        self.osmosdr_sink.set_if_gain(self.IF_gain, 0)
        self.osmosdr_sink.set_bb_gain(20, 0)
        self.osmosdr_sink.set_antenna('', 0)
        self.osmosdr_sink.set_bandwidth(self.sdr_bandwidth, 0)

        if waveform == 2:
            tb.connect(self.source, self.freq_mod, self.osmosdr_sink)
        else:
            tb.connect(self.source, self.osmosdr_sink)

        tb.start()
        time.sleep(self.t_jamming)
        tb.stop()
        tb.wait()

def main():
    """
    This is the main function. We instantiate a jammer object and call the methods
    to perform jamming accordingly
    """
    jamming = int(input("Select Type of Jamming (1=proative, 2=reactive): "))
    jammer = int(input("Select Jammer Type (1=constant, 2=sweeping, 3=random channel hopping): "))
    waveform = int(input("Select Jamming waveform (1=modulated sine, 2=swept sine, 3=gaussian noise): " ))
    power = int(input("Enter Jammer transmit power in dBm (Min = -40dBm, Max = 13dBm): "))
    t_jamming = int(input("Enter channel jamming duration in sec: "))
    ch_dist = int(input("Enter center frequency hopping width in MHz (Min = 1MHz, Max = 20MHz): ")) * 10e5			# Channel hopping
    init_freq = 2412e6
    lst_freq = 2484e6
    n_channels = (lst_freq - init_freq)//ch_dist
    threshold = 0.0002

    my_Jammer = JamRF(jamming, jammer, waveform, power, t_jamming, ch_dist)

    if jamming == 1:
        if jammer == 1:
            freq = int(input("Enter the frequency to Jam in MHz: ")) * 10e5
            my_Jammer.jam(freq)
        elif jammer == 2:
            channel = 1
            while True:
                freq = my_Jammer.set_frequency(init_freq,channel)
                my_Jammer.jam(freq)
                channel = 1 if channel > n_channels else channel + 1
        elif jammer == 3:
            while True:
                channel = randint(1, n_channels + 1)
                freq = my_Jammer.set_frequency(init_freq,channel)
                my_Jammer.jam(freq)
        else:
            print("Invalid Jammer selection")

    elif jamming == 2:
        if jammer == 1:
            freq = int(input("Enter the frequency to Jam in MHz: ")) * 10e5
            my_Jammer.sense(freq)
            rx_power = my_Jammer.detect()
            if rx_power > threshold:
                my_Jammer.jam(freq)
        elif jammer == 2:
            channel = 1
            while True:
                freq = my_Jammer.set_frequency(init_freq,channel)
                my_Jammer.sense(freq)
                rx_power = my_Jammer.detect()
                if rx_power > threshold:
                    my_Jammer.jam(freq)
                channel = 1 if channel > n_channels else channel + 1
        elif jammer == 3:
            while True:
                channel = randint(1, n_channels + 1)
                freq = my_Jammer.set_frequency(init_freq,channel)
                my_Jammer.sense(freq)
                rx_power = my_Jammer.detect()
                if rx_power > threshold:
                    my_Jammer.jam(freq)
        else:
            print("Invalid Jammer selection")

    else:
        print("Invalid Jamming Type Selection")

if __name__ == '__main__':
    main()
