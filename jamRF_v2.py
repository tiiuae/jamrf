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
    jamming_type = input("Select Type of Jamming (1|proative, 2|reactive): ").lower()
    jammer = input("Select Jammer Type (1|constant, 2|sweeping, 3|hopping): ").lower()
    waveform = input("Select Jamming waveform (1|mod_sine, 2|swept_sine, 3|noise): " ).lower()
    power = int(input("Enter Jammer transmit power in dBm (Min = -40dBm, Max = 13dBm): "))
    t_jamming = int(input("Enter channel jamming duration in sec: "))
    duration = int(input("Enter total runtime duration in sec: "))
    if t_jamming > duration:
        t_jamming = duration

    if jammer != 'constant' and jammer != '1':
        band = int(input("Select Frequency Band (1=2.4GHz, 2=5GHz)"))
        if band == 1:
            ch_dist = int(input("Enter distance between adjacent channels in MHz (Min = 1MHz, Max = 20MHz): ")) * 10e5
            init_freq = 2412e6
            lst_freq = 2484e6
        elif band == 2:
            ch_dist = 20e6
            allocation = int(input("Select channel allocation (1=UNII-1, 2=UNII-2a, 3=UNII-2c, 4=UNII-3)"))
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
    else:
        pass

    if jammer == 'constant' or jammer == '1':
        freq = int(input("Enter the frequency to Jam in MHz: ")) * 10e5
        constant(jamming_type, duration, waveform, power, t_jamming, freq)
    elif jammer == 'sweeping' or jammer == '2':
        sweeping(jamming_type, duration, waveform, power, t_jamming, init_freq, lst_freq, ch_dist)
    elif jammer == 'hopping' or jammer == '3':
        hopping(jamming_type, duration, waveform, power, t_jamming, init_freq, lst_freq, ch_dist)
    else:
        print('invalid selection')
if __name__ == '__main__':
    main()
