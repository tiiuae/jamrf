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
    """
    This is the main function. In this program we evaluate jammer performance for
    different types of scenarios.
    """
    jamming_types = ['proactive', 'reactive']
    jammers = ['constant', 'sweeping', 'hopping']
    waveforms = ['single_tone', 'QPSK_mod', 'noise']
    power_vals = list(range(-4,15,2))
    t_jamming_vals = [5,10,15,20]
    ch_dists = [ch_dist*10e5 for ch_dist in range(5,25,5)]
    init_freq = 2412e6
    lst_freq = 2484e6
    duration = 300
    n_runs = 10

    # Experiment 1: PRR vs power using constant jammer
    # for waveform in waveforms:
    #     for power in power_vals:
    #         for run in range(n_runs):
    #             t_jamming = 27.5
    #             freq = 2462e6
    #             constant(jamming_types[0], duration, waveform, power, t_jamming, freq)

    # Experiment 2: PRR vs channel distance for proactive
    # for waveform in waveforms[2:3]:
    #     for ch_dist in ch_dists[3:4]:
    #         for run in range(n_runs):
    #             power = 5
    #             t_jamming = 5
    #             sweeping(jamming_types[0], duration, waveform, power, t_jamming, init_freq, lst_freq, ch_dist)

    #Experiment 3: PRR vs channel distance for reactive
    # for waveform in waveforms:
    #     for ch_dist in ch_dists:
    #         for run in range(n_runs):
    #             power = 5
    #             t_jamming = 5
    #             sweeping(jamming_types[1], duration, waveform, power, t_jamming, init_freq, lst_freq, ch_dist)

    # Experiment 4: PRR vs Duration for Proactive jammers
    # for jammer in jammers[2:3]:
    #     for t_jamming in t_jamming_vals[3:4]:
    #         for run in range(n_runs):
    #             waveform = waveforms[1]
    #             power = 6
    #             ch_dist = 20*10e5
    #             if jammer == 'sweeping':
    #                 sweeping(jamming_types[0], duration, waveform, power, t_jamming, init_freq, lst_freq, ch_dist)
    #             elif jammer == 'hopping':
    #                 hopping(jamming_types[0], duration, waveform, power, t_jamming, init_freq, lst_freq, ch_dist)

    # Experiment 5: PRR vs t_jamming for Reactive jammers
    for jammer in jammers[2:3]:
        for t_jamming in t_jamming_vals[3:4]:
            for run in range(n_runs-3):
                waveform = waveforms[1]
                power = 6
                ch_dist = 20*10e5
                if jammer == 'sweeping':
                    sweeping(jamming_types[1], duration, waveform, power, t_jamming, init_freq, lst_freq, ch_dist)
                elif jammer == 'hopping':
                    hopping(jamming_types[1], duration, waveform, power, t_jamming, init_freq, lst_freq, ch_dist)

if __name__ == '__main__':
    main()
