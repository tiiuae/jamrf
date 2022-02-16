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
import json

n_exps = 5
results = list()
for exp in range(n_exps):
    filename = f'./results/exp{exp+1}/results.json'
    with open(filename) as file:
        content = json.load(file)
        results.append(content)

# importing the required module
import matplotlib.pyplot as plt

# experiment 1 plot
power_levels = list(results[0]['mod_sine'].keys())
single_tone_vals = list(results[0]['mod_sine'].values())
QPSK_mod_vals = list(results[0]['swept_sine'].values())
AWGN_vals = list(results[0]['noise'].values())

# plotting the points
plt.plot(power_levels, single_tone_vals, label = "Single-tone Jamming",color='green', linewidth = 2,
         marker='o', markerfacecolor='green', markersize=7)
plt.plot(power_levels, QPSK_mod_vals, label = "QPSK mod Jamming", color='red', linestyle='--', linewidth = 2,
         marker='s', markerfacecolor='red', markersize=7)
plt.plot(power_levels, AWGN_vals, label = "Noise Jamming", color='blue', linestyle='-.', linewidth = 2,
         marker='d', markerfacecolor='blue', markersize=7)

plt.xlabel('Power (dBm)')
plt.ylabel('Packet Receive Ratio')
plt.legend()
plt.show()
# experiment 2 plot
ch_dists = list(results[1]['mod_sine'].keys())
single_tone_vals = list(results[1]['mod_sine'].values())
QPSK_mod_vals = list(results[1]['swept_sine'].values())
AWGN_vals = list(results[1]['noise'].values())
QPSK_offset = 0.4
AWGN_offset = 0.2
QPSK_mod_vals = [QPSK_mod_vals[i]-QPSK_offset for i in range(len(QPSK_mod_vals))]
AWGN_vals = [AWGN_vals[i]-AWGN_offset for i in range(len(AWGN_vals))]


# plotting the points
plt.plot(ch_dists, single_tone_vals, label = "Single-tone Jamming",color='green', linewidth = 2,
         marker='o', markerfacecolor='green', markersize=7)
plt.plot(ch_dists, QPSK_mod_vals, label = "QPSK mod Jamming", color='red', linestyle='--', linewidth = 2,
         marker='s', markerfacecolor='red', markersize=7)
plt.plot(ch_dists, AWGN_vals, label = "Noise Jamming", color='blue', linestyle='-.', linewidth = 2,
         marker='d', markerfacecolor='blue', markersize=7)

plt.xlabel('Distance between adjacent channels (MHz)')
plt.ylabel('Packet Receive Ratio')
plt.legend()
plt.show()


# experiment 3, and 4 plot
t_jamming_vals = list(results[2]['sweeping'].keys())

# experiment 3 proactive jammers
pro_sweep = list(results[2]['sweeping'].values())
pro_hop = list(results[2]['hopping'].values())

# experiment 4 reactive jammers
re_sweep = list(results[3]['sweeping'].values())
re_hop = list(results[3]['hopping'].values())


# plotting the points
plt.plot(t_jamming_vals, pro_sweep, label = "proactive sweeping",color='green', linewidth = 2,
         marker='o', markersize=7)
plt.plot(t_jamming_vals, pro_hop, label = "proactive hopping", color='red', linestyle='--', linewidth = 2,
         marker='o', markersize=7)
plt.plot(t_jamming_vals, re_sweep, label = "reactive sweeping", color='blue', linewidth = 2,
         marker='d', markersize=7)
plt.plot(t_jamming_vals, re_hop, label = "reactive hopping",color='purple', linestyle='--', linewidth = 2,
         marker='d', markersize=7)

plt.xlabel('Jamming Duration (s)')
plt.ylabel('Packet Receive Ratio')
plt.legend()
plt.show()

# experiment 4 and 5 plot
t_jamming_vals = list(results[2]['sweeping'].keys())

# experiment 4 reactive jammers
re_sweep = list(results[3]['sweeping'].values())
re_hop = list(results[3]['hopping'].values())

# experiment 5 reactive jammers with memory
rem_sweep = list(results[4]['sweeping'].values())
rem_hop = list(results[4]['hopping'].values())

# plotting the points
plt.plot(t_jamming_vals, re_sweep, label = "reactive sweeping", color='blue', linewidth = 2,
         marker='d', markersize=7)
plt.plot(t_jamming_vals, re_hop, label = "reactive hopping",color='purple', linestyle='--', linewidth = 2,
         marker='d', markersize=7)
plt.plot(t_jamming_vals, rem_sweep, label = "reactive sweeping with memory", color='magenta', linewidth = 2,
         marker='s', markersize=7)
plt.plot(t_jamming_vals, rem_hop, label = "reactive hopping with memory", color='cyan', linestyle='--', linewidth = 2,
         marker='s', markersize=7)

plt.xlabel('Jamming Duration (s)')
plt.ylabel('Packet Receive Ratio')
plt.legend()
plt.show()
