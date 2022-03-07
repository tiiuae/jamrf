#!/usr/bin/env python
# coding:utf-8
"""
name        : networks.py,
version     : 1.0.0,
url         : https://github.com/abubakar-sani/RFF,
license     : MIT License,
copyright   : Copyright 2021 by Abubakar Sani Ali, Khalifa University,
author      : Abubakar Sani Ali,
email       : engrabubakarsani@gmail.com,
date        : 9/5/2021,
description : Deep Learning classifiers for RFF,
"""

#%% Loading libraries
import numpy as np
import pandas as pd
import seaborn as sns
from tqdm.notebook import tqdm
import matplotlib.pyplot as plt
import torch
import torchvision
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torchvision import transforms, utils, datasets
from torch.utils.data import Dataset, DataLoader, SubsetRandomSampler
from sklearn.metrics import confusion_matrix, accuracy_score

# Define a 1D CNN Network with input
#o_h =  [4,26,76]
#o_w = [1,1,1]
class Network_1D(nn.Module):
    def __init__(self):
        super().__init__()
        self.block1 = self.conv_block(c_in=2, c_out=128, kernel_size=7)
        self.block2 = self.conv_block(c_in=128, c_out=128, kernel_size=7)
        self.block3 = self.conv_block(c_in=128, c_out=128, kernel_size=5)
        self.block4 = self.fc_block(f_in=128*84, f_out=256)
        self.block5 = self.fc_block(f_in=256, f_out=128)
        self.out = self.out_block(f_in=128, f_out=2)
        self.maxpool = nn.MaxPool1d(kernel_size=2, stride=1)

    def forward(self, x):
        # Fist block
        x = self.block1(x)
        x = self.block3(x)
        x = self.maxpool(x)
        # 2nd block
        x = self.block2(x)
        x = self.block3(x)
        x = self.maxpool(x)
        # 3rd block
        x = self.block2(x)
        x = self.block3(x)
        x = self.maxpool(x)
        # 4th block
        x = self.block2(x)
        x = self.block3(x)
        x = self.maxpool(x)
        # Flattening block
        x = x.view(-1,128*84)
        x = self.block4(x)
        x = self.block5(x)
        x = self.out(x)
        return x

    def conv_block(self, c_in, c_out, **kwargs):
        seq_block = nn.Sequential(
            nn.Conv1d(in_channels=c_in, out_channels=c_out, **kwargs),
            #nn.BatchNorm1d(num_features=c_out),
            nn.ReLU(),
        )
        return seq_block

    def fc_block(self, f_in, f_out):
        seq_block = nn.Sequential(
            nn.Linear(in_features=f_in, out_features=f_out),
            nn.ReLU(),
        )
        return seq_block

    def out_block(self, f_in, f_out):
        seq_block = nn.Sequential(
            nn.Linear(in_features=f_in, out_features=f_out),
            nn.LogSoftmax(dim=1),
        )
        return seq_block

# Define a 2D CNN Network with input length by 2
class Network_2D(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(in_channels=1, out_channels=160, kernel_size=4, padding=2, stride=2)
        self.conv2 = nn.Conv2d(in_channels=160, out_channels=320, kernel_size=(10,1), stride = 2)
        self.fc1 = nn.Linear(in_features=320*4*1, out_features=120)
        self.fc2 = nn.Linear(in_features=120, out_features=240)
        self.fc3 = nn.Linear(in_features=240, out_features=480)
        self.fc4 = nn.Linear(in_features=480, out_features=240)
        self.fc5 = nn.Linear(in_features=240, out_features=120)
        self.fc6 = nn.Linear(in_features=120, out_features=60)
        self.out = nn.Linear(in_features=60, out_features=1)

    def forward(self, x):
        # (1) input layer
        x = x
        # (2) hidden conv1 layer
        x = self.conv1(x)
        x = F.relu(x)
        x = F.max_pool2d(x, kernel_size=(3,2), stride=2)
        # (3) hidden conv2 layer
        x = self.conv2(x)
        x = F.relu(x)
        x = F.max_pool2d(x, kernel_size=(6,1), stride=2)
        # (4) hidden linear layer
        # flattening t
        x = x.view(-1, 320*4*1)
        x = self.fc1(x)
        x = F.relu(x)
        # (5) hidden linear layer
        x = self.fc2(x)
        x = F.relu(x)
        # (6) hidden linear layer
        x = self.fc3(x)
        x = F.relu(x)
        # (7) hidden linear layer
        x = self.fc4(x)
        x = F.relu(x)
        # (8) hidden linear layer
        x = self.fc5(x)
        x = F.relu(x)
        # (9) hidden linear layer
        x = self.fc6(x)
        x = F.relu(x)
        # (10) output layer
        x = self.out(x)
        #x = torch.sigmoid(x)
        return x

#%% Define Discriminator
class Discriminator(nn.Module):
    def __init__(self, nchannels, nfeats):
        super(Discriminator, self).__init__()

        # input is (nchannels) x 128 x 2
        self.conv1 = nn.Conv2d(nchannels, nfeats, 4, 2, 1, bias=False)
        # state size. (nfeats) x 64 x 1

        self.conv2 = nn.Conv2d(nfeats, nfeats * 2, (4,3), 2, 1, bias=False)
        self.bn2 = nn.BatchNorm2d(nfeats * 2)
        # state size. (nfeats*2) x 32 x 1

        self.conv3 = nn.Conv2d(nfeats * 2, nfeats * 4, (4,3), 2, 1, bias=False)
        self.bn3 = nn.BatchNorm2d(nfeats * 4)
        # state size. (nfeats*4) x 16 x 1

        self.conv4 = nn.Conv2d(nfeats * 4, nfeats * 8, (4,3), 2, 1, bias=False)
        self.bn4 = nn.BatchNorm2d(nfeats * 8)
        # state size. (nfeats*8) x 8 x 1

        self.conv5 = nn.Conv2d(nfeats * 8, nfeats * 8, (4,3), 2, 1, bias=False)
        self.bn5 = nn.BatchNorm2d(nfeats * 8)
        # state size. (nfeats*8) x 4 x 1

        self.conv6 = nn.Conv2d(nfeats * 8, 1, (4,1), 1, 0, bias=False)
        # state size. 1 x 1 x 1

    def forward(self, x):
        x = F.leaky_relu(self.conv1(x), 0.2)
        x = F.leaky_relu(self.bn2(self.conv2(x)), 0.2)
        x = F.leaky_relu(self.bn3(self.conv3(x)), 0.2)
        x = F.leaky_relu(self.bn4(self.conv4(x)), 0.2)
        x = F.leaky_relu(self.bn5(self.conv5(x)), 0.2)
        x = self.conv6(x)

        return x.view(-1, 1)
