#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
# Author: abubakar
# GNU Radio version: 3.8.1.0

from JamRF import constant, sweeping, hopping

def main():
    jamming_type = input("Select Type of Jamming (proative, reactive): ")
    jammer = input("Select Jammer Type (constant, sweeping, hopping): ")
    waveform = input("Select Jamming waveform (mod_sine, swept_sine, noise): " )
    power = int(input("Enter Jammer transmit power in dBm (Min = -40dBm, Max = 13dBm): "))
    t_jamming = int(input("Enter channel jamming duration in sec: "))
    ch_dist = int(input("Enter distance between adjacent channels in MHz (Min = 1MHz, Max = 20MHz): ")) * 10e5			# Channel hopping
    init_freq = 2412e6
    lst_freq = 2484e6
    duration = 600

    if jammer == 'constant':
        constant(waveform, power, t_jamming, freq)
    elif jammer == 'sweeping':
        sweeping(jamming_type, duration, waveform, power, t_jamming, init_freq, lst_freq, ch_dist)
    elif jammer == 'hopping':
        hopping(jamming_type, duration, waveform, power, t_jamming, init_freq, lst_freq, ch_dist)
    else:
        print('invalid selection')
if __name__ == '__main__':
    main()
