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
from statistics import mean
duration = 300
n_runs = 10
transfer = list()
for run in range(n_runs):
    filename = f'./results/exp0/log_{run+1}.json'
    with open(filename) as file:
        content = json.load(file)
        transfer.append(content['end']['sum']['bytes'])

avr_transfer = mean(transfer)

#%% Optimal waveform
waveforms = ['mod_sine','swept_sine','noise']
power_levels = list(range(-4,15,2))
i = 0
exp1 = {}
for waveform in waveforms:
    i = i+1
    j = 0
    pwr = {}
    for power_level in power_levels:
        j = j+1    
        transfer = list()
        for run in range(n_runs):
            filename = f'./results/exp1/log_{i}_{j}_{run+1}.json'
            with open(filename) as file:
                content = json.load(file)
                try:
                    transfer.append(content['end']['sum']['bytes'])
                except KeyError:
                    pass
        pwr[f'{power_level}'] = mean(transfer)/(avr_transfer*30/5)
    exp1[f'{waveform}'] = pwr
        
print(exp1)

#%% Optimal Distance between two adjacent channels
waveforms = ['mod_sine','swept_sine','noise']
channel_dists = [5,10,15,20]#list(range(5,20,5))
i = 0
exp2 = {}
for waveform in waveforms:
    i = i+1
    j = 0
    cdst = {}
    for channel_dist in channel_dists:
        j = j+1    
        transfer = list()
        for run in range(n_runs):
            filename = f'./results/exp2/log_{i}_{j}_{run+1}.json'
            with open(filename) as file:
                content = json.load(file)
                try:
                    transfer.append(content['end']['sum']['bytes'])
                except KeyError:
                    pass
                # except TypeError:
                #     print(f'log_{i}_{j}_{run+1}.json has error')
                # except json.JSONDecodeError:
                #     print(f'log_{i}_{j}_{run+1}.json has error')
        cdst[f'{channel_dist}'] = mean(transfer)/(avr_transfer*180/5)
    exp2[f'{waveform}'] = cdst
    
print(exp2)

#%% Performance of proactive jammers
jammers = ['sweeping','hopping']
t_jamming_vals = [5,10,15,20]
i = 0
exp3 = {}
for jammer in jammers:
    i = i+1
    j = 0
    proactive = {}
    for t_jamming in t_jamming_vals:
        j = j+1    
        transfer = list()
        for run in range(n_runs):
            filename = f'./results/exp3/log_{i}_{j}_{run+1}.json'
            with open(filename) as file:
                content = json.load(file)
                try:
                    transfer.append(content['end']['sum']['bytes'])
                except KeyError:
                    pass
                # except TypeError:
                #     print(f'log_{i}_{j}_{run+1}.json has error')
                # except json.JSONDecodeError:
                #     print(f'log_{i}_{j}_{run+1}.json has error')
        proactive[f'{t_jamming}'] = mean(transfer)/(avr_transfer*300/5)
    exp3[f'{jammer}'] = proactive
    
print(exp3)

#%% Performance of reactive jammers
jammers = ['sweeping','hopping']
t_jamming_vals = [5,10,15,20]
i = 0
exp4 = {}
for jammer in jammers:
    i = i+1
    j = 0
    reactive = {}
    for t_jamming in t_jamming_vals:
        j = j+1    
        transfer = list()
        for run in range(n_runs):
            filename = f'./results/exp4/log_{i}_{j}_{run+1}.json'
            with open(filename) as file:
                content = json.load(file)
                try:
                    transfer.append(content['end']['sum']['bytes'])
                except KeyError:
                    pass
        reactive[f'{t_jamming}'] = mean(transfer)/(avr_transfer*300/5)
    exp4[f'{jammer}'] = reactive
    
print(exp4)

#%% Performance of Reactive jammers with memory
jammers = ['sweeping','hopping']
t_jamming_vals = [5,10,15,20]
i = 0
exp5 = {}
for jammer in jammers:
    i = i+1
    j = 0
    reactive_m = {}
    for t_jamming in t_jamming_vals:
        j = j+1    
        transfer = list()
        for run in range(n_runs):
            filename = f'./results/exp5/log_{i}_{j}_{run+1}.json'
            with open(filename) as file:
                content = json.load(file)
                try:
                    transfer.append(content['end']['sum']['bytes'])
                except KeyError:
                    pass
        reactive_m[f'{t_jamming}'] = mean(transfer)/(avr_transfer*300/5)
    exp5[f'{jammer}'] = reactive_m
    
print(exp5)

#%% Saving results
experiments = [exp1, exp2, exp3, exp4, exp5]
i = 0
for experiment in experiments:
    i = i+1
    with open(f'./results/exp{i}/results.json', 'w') as file:
        file.write(json.dumps(experiment))
