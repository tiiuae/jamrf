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
import yaml
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
    print(f"\nThe frequency currently jammed is: {freq/(10e5)}MHz")
    samp_rate = 20e6		            # Sample Rate
    sdr_bandwidth = 20e6	            # Hackrf SDR Bandwidth
    RF_gain, IF_gain = set_gains(power)    # Hackrf SDR antenna gain

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
    with open("output.bin", mode = 'rb') as file:
        fileContent = file.read()
        samples = np.memmap("output.bin", mode = "r", dtype = np.float32)

    p = 0.5 * mean(samples)
    return p

##################################################################################
# Main Function
##################################################################################

if __name__ == "__main__":
    # Global options
    stream = open("config_v1.yaml", 'r')
    parameters = yaml.load_all(stream)

    for par in parameters:     
        band = par["band"]
        jammer = par["jammer"]
        jamming = par["jamming"]
        waveform = par["waveform"]
        power = par["power"]
        t_jamming = par["t_jamming"]
        duration = par["duration"]
        ch_dist = par["ch_dist"]
        freq = par["freq"]
        allocation = par["allocation"]
            
    # Special options
    if jammer != 1:
        if band == 1:
            ch_dist = ch_dist * 10e5
            init_freq = 2412e6
            lst_freq = 2484e6
        elif band == 2:
            ch_dist = 20e6
            if allocation == 1:
                init_freq = 5180e6
                lst_freq = 5240e6
            elif allocation == 2:
                init_freq = 5260e6
                lst_freq = 5320e6
            elif allocation == 3:
                init_freq = 5500e6
                lst_freq = 5720e6
            elif allocation == 4:
                init_freq = 5745e6
                lst_freq = 5825e6
            else:
                print('Invalid selection')
        else:
            print('Invalid selection')
        n_channels = (lst_freq - init_freq)//ch_dist
        if t_jamming > duration:
            t_jamming = duration
    if jamming == 2:
        t_sensing = 0.05
        threshold = 0.0002
    
    # Starting RF Jamming
    if jammer == 1:
        freq = freq * 10e5
        if jamming == 1:
            jam(freq, waveform, power, t_jamming)
        elif jamming == 2:
            # Sensing Channel
            sense(freq, t_sensing)
            rx_power = detect()
            print(rx_power)
            # If channel is active then jam it
            if rx_power > threshold:
                jam(freq, waveform, power, t_jamming)

        else:
            print("Invalid jamming option selection")

    elif jammer == 2:
        channel = 1         # Initial Channel @ 2.412GHz
        start_time = time.time()
        while True:
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
            else:
                print("Invalid jamming option selection")
            # Go to next channel
            channel = 1 if channel > n_channels else channel + 1
            # Checking elapsed time
            jamming_time_per_run = time.time() - start_time
            if jamming_time_per_run >= duration:
                break

    elif jammer == 3:
        start_time = time.time()
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
            else:
                print("Invalid jamming option selection")    
            # Checking elapsed time
            jamming_time_per_run = time.time() - start_time
            if jamming_time_per_run >= duration:
                break
                
    else:
        print("invalid jammer selection")
