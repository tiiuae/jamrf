#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Hackrf Dataset Preprocessing Module
# Author: Abubakar Sani Ali
# GNU Radio version: 3.8.1.0

###################################################################################
# Importing Libraries
###################################################################################
import math
import os
import time
import yaml
from statistics import mean
import sys
import numpy as np
from random import randint


def get_labeled_data(cond, x1, x2, stride, length):
    cond = 0 if cond == 'idle' else 1
    # Breaking data into batches
    t_samples = len(x1)
    n_samples = math.floor((t_samples - length) / stride)
    x1 = x1[0:t_samples]
    x2 = x2[0:t_samples]
    print(f'the number of samples is: {n_samples}')
    device_data = np.zeros((n_samples, 2, length), dtype='float32')

    # Compute every sample
    for sample in range(n_samples):
        # Filter out the ith sample
        x1 = x1[sample * stride: sample * stride + length]
        x2 = x2[sample * stride: sample * stride + length]

        # Store data into the train set
        if x1.shape[0] % length == 0:
            for i in range(len(x1)):
                device_data[sample][0][i] = x1[i]
                device_data[sample][1][i] = x2[i]
    print(device_data.shape)
    # Add target label to the samples, where target label = device_id
    labeled = []
    for sample in device_data:
        line = [sample, cond]
        labeled.append(line)
    labeled = np.array(labeled, dtype=object)

    return labeled


def get_samples(cond, length, stride):
    data = None
    data_file = f'{cond}IQ_data.bin'
    with open(data_file, mode='rb') as file:
        fileContent = file.read()
        samples = np.memmap(data_file, mode="r", dtype=np.float32)
        x1 = samples.real
        x2 = samples.imag

        # Returning labelled data containing samples of length = length with a sliding window = stride
        labeled = get_labeled_data(cond, x1, x2, stride, length)
        # Concatenate the labelled samples
        if data is None:
            data = labeled
        else:
            data = np.concatenate((data, labeled))

    return data


def load_dataset(cond, length, stride):
    processed_data_dir = './processed_dataset'
    idle_directory = f'{processed_data_dir}/idle_state/'
    active_directory = f'{processed_data_dir}/active_state/'

    # Process the dataset and generate the raw numpy (to processing it every run)
    if cond == 'idle':
        if not os.path.isfile(f'{idle_directory}/dataset{length}_{stride}.npy'):
            labeled = get_samples(cond, length, stride)

            if not os.path.exists(idle_directory):
                os.makedirs(idle_directory)

            np.save(f'{idle_directory}/dataset{length}_{stride}', labeled)
    else:
        if not os.path.isfile(f'{active_directory}/dataset{length}_{stride}.npy'):
            # Load data for active channel
            labeled = get_samples(cond, length, stride)
            if not os.path.exists(active_directory):
                os.makedirs(active_directory)

            np.save(f'{active_directory}/dataset{length}_{stride}', labeled)

    # Extract sample and targets column (If data already exists)
    if cond == 'idle':
        np_data = np.load(f'{idle_directory}/dataset{length}_{stride}.npy', allow_pickle=True)
    else:
        np_data = np.load(f'{active_directory}/dataset{length}_{stride}.npy', allow_pickle=True)

    return np_data

