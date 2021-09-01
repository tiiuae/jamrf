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
n_runs = 10
transfer = list()
for run in range(n_runs):
    filename = f'./results/exp0/log_{run+1}.json'
    with open(filename) as file:
        content = list(json.load(file))
        print(content['end']['sum']['bytes'])
        #transfer.append(content['end']['sum']['bytes'])

#transfer = content['end']['sum']['bytes']
#print(f'the total transfer is {transfer/10e5} MB')
