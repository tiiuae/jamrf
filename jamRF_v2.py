#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
# Author: Abubakar Sani Ali
# GNU Radio version: 3.8.1.0
import yaml
from JamRF import constant, sweeping, hopping


def main():
    # Jammer options
    config_file = open("config_v2.yaml")
    options = yaml.load(config_file, Loader=yaml.FullLoader)
    jammer = options.get("jammer")
    # jamming = options.get("jamming")
    # waveform = options.get("waveform")
    # power = options.get("power")
    band = options.get("band")
    freq = options.get("freq")
    ch_dist = options.get("ch_dist")
    allocation = options.get("allocation")
    t_jamming = options.get("t_jamming")
    duration = options.get("duration")

    if jammer != 1:
        if band == 1:
            init_freq = 2412e6
            lst_freq = 2484e6
        elif band == 2:
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
        # if t_jamming > duration:
        #     t_jamming = duration

    if jammer == 1:
        constant(options)
    elif jammer == 2:
        sweeping(init_freq, lst_freq, options)
    elif jammer == 3:
        hopping(init_freq, lst_freq, options)
    else:
        print('invalid selection')


if __name__ == '__main__':
    main()
