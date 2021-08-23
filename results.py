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
    """Constant
    jamming_types = ['proactive', 'reactive']
    jammers = ['constant', 'sweeping', 'hopping']
    waveforms = ['mod_sine', 'swept_sine', 'noise']
    power_vals = [-40:14]
    t_jamming_vals = [1:30:2]
    ch_dists = [1:20] * 10e5
    init_freq = 2412e6
    lst_freq = 2484e6
    duration = 600

    # Experiment 1: PRR vs power using constant jammer
    for waveform in waveforms:
        for power in power_vals:
            t_jamming = 30
            freq = 2462e9
            constant(waveform, power, t_jamming, freq)

    # Experiment 2: PRR vs channel distance
    for waveform in waveforms:
        for ch_dist in ch_dists:
            power = 10
            t_jamming = 10
            sweeping(jamming_type, duration, waveform, power, t_jamming, init_freq, lst_freq, ch_dist)

    # Experiment 3: PRR vs Duration for Proactive jammers
    for jammer in jammers[1:]:
        for t_jamming in t_jamming_vals:
            jamming_type = jamming_types[0]
            waveform = waveforms[1]
            power = 6
            ch_dist = 20
            if jammer == 'sweeping':
                sweeping(jamming_type, duration, waveform, power, t_jamming, init_freq, lst_freq, ch_dist)
            elif jammer = 'hopping':
                hopping(jamming_type, duration, waveform, power, t_jamming, init_freq, lst_freq, ch_dist)

    # Experiment 4: PRR vs t_jamming for Reactive jammers
    for jammer in jammers[1:]:
        for t_jamming in t_jamming_vals:
            jamming_type = jamming_types[1]
            waveform = waveforms[1]
            power = 6
            ch_dist = 20
            if jammer == 'sweeping':
                sweeping(jamming_type, duration, waveform, power, t_jamming, init_freq, lst_freq, ch_dist)
            elif jammer = 'hopping':
                hopping(jamming_type, duration, waveform, power, t_jamming, init_freq, lst_freq, ch_dist)

if __name__ == '__main__':
    main()
