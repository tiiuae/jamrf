#!/usr/bin/env python
# coding:utf-8
"""
name        : DL_models.py,
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
import sys
sys.path.insert(1, '/home/abubakar/KU/PL_authentication/Classifiers')
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
from torchvision import transforms, utils, datasets, models
from torch.utils.data import Dataset, DataLoader, SubsetRandomSampler
from sklearn.metrics import confusion_matrix, accuracy_score

from lib.train_test.CNN_train_test import train, test
from lib.networks.CNN_networks import Network_1D, Network_2D, Discriminator
from lib.data.dataloader import get_oracle_tdl, get_uav_tdl

def discriminatorNet(uavs,intruders,dimension='2D',cond='raw',length=128,stride=1,BATCH_SIZE=64,EPOCHS=50,LEARNING_RATE=0.001,device=torch.device("cpu")):
	# Raw dataset
	print('\nTraining with Discriminator')
	if cond == 'raw':
		distance = 6
		train_loader, val_loader, test_loader = get_uav_tdl(uavs,distance,dimension,intruders,length,stride,BATCH_SIZE)
		# Training network
		print('\nTraining with raw dataset')
		model_raw = Discriminator(1, 48).to(device)
		print(model_raw)
		criterion = nn.BCEWithLogitsLoss()
		optimizer = optim.Adam(model_raw.parameters(), lr=LEARNING_RATE)
		model_raw = train(EPOCHS,train_loader,val_loader,model_raw,device,criterion,optimizer)
		# Testing the trained network
		test(test_loader,model_raw,device,length)

	# Noisy dataset
	else:
		SNR_dB = list(range(-10,35,5))
		for SNR in SNR_dB:
			train_loader, val_loader, test_loader = get_uav_tdl(dimension,intruder,cond,length,stride,BATCH_SIZE,SNR)
		   	# Training network
			print(f'\nTraining with noisy dataset with SNR={SNR}dB')
			model_noisy = Discriminator(1, 48).to(device)
			print(model_noisy)
			criterion = nn.BCEWithLogitsLoss()
			optimizer = optim.Adam(model_noisy.parameters(), lr=LEARNING_RATE)
			model_noisy = train(EPOCHS,train_loader,model_noisy,device,criterion,optimizer)
			# Testing the trained network
			test(test_loader,model_noisy,device,criterion,length)

def simpleConvNet(dimension='1D',intruder=1,cond='raw',length=128,stride=1,BATCH_SIZE=64,EPOCHS=50,LEARNING_RATE=0.001,device=torch.device("cpu")):
	# Raw dataset
	print('\nTraining with simple ConvNet')
	if cond == 'raw':
		#train_loader, val_loader, test_loader, y_test = get_uav_tdl(dimension,intruder,cond,length,stride,BATCH_SIZE)
		distance = 6
		n_uavs = 2
		train_loader, val_loader, test_loader = get_uav_tdl(n_uavs,distance,dimension,intruder,length,stride,BATCH_SIZE)

		# Training network
		print('\nTraining with raw dataset')
		if dimension == '1D':
			model_raw = Network_1D()
		else:
			model_raw = Network_2D()
		model_raw.to(device)
		print(model_raw)
		criterion = nn.BCEWithLogitsLoss()
		optimizer = optim.Adam(model_raw.parameters(), lr=LEARNING_RATE)
		model_raw = train(EPOCHS,train_loader,val_loader,model_raw,device,criterion,optimizer)
		# Testing the trained network
		test(test_loader,model_raw,device,criterion,length)

	# Noisy dataset
	else:
		SNR_dB = list(range(-10,35,5))
		for SNR in SNR_dB:
			train_loader, val_loader, test_loader = get_uav_tdl(algo,dimension,intruder,cond,length,stride,BATCH_SIZE,SNR)
		   	# Training network
			print(f'\nTraining with noisy dataset with SNR={SNR}dB')
			if dimension == '1D':
				model_noisy = Network_1D()
			else:
				model_noisy = Network_2D()
			model_noisy.to(device)
			print(model_noisy)
			criterion = nn.BCEWithLogitsLoss()
			optimizer = optim.Adam(model_noisy.parameters(), lr=LEARNING_RATE)
			model_noisy = train(EPOCHS,train_loader,model_noisy,device,criterion,optimizer)
			# Testing the trained network
			test(test_loader,model_noisy,device,criterion,length)

def pretrainedNet(algo,dimension='2D',intruder=1,cond='raw',length=224,stride=1,BATCH_SIZE=64,EPOCHS=50,LEARNING_RATE=0.001,device=torch.device("cpu")):
	# Raw dataset
	print('\nTraining with VGG16')
	if cond == 'raw':
		train_loader, val_loader, test_loader = get_uav_tdl(algo,dimension,intruder,cond,length,stride,BATCH_SIZE)
		# Training network
		print('\nTraining with raw dataset')
		model_raw = model_raw = models.vgg16(pretrained=True)
		# Freeze model weights
		for param in model_raw.parameters():
		   param.requires_grad = False

		num_ftrs = model_raw.classifier[6].in_features
		# Here the size of each output sample is set to 2.
		# Alternatively, it can be generalized to nn.Linear(num_ftrs, len(class_names)).
		model_raw.classifier[6] = nn.Linear(num_ftrs, 2)
		model_raw.to(device)
		print(model_raw)
		criterion = nn.BCEWithLogitsLoss()
		optimizer = optim.Adam(model_raw.parameters(), lr=LEARNING_RATE)
		model_raw = train(EPOCHS,train_loader,val_loader,model_raw,device,criterion,optimizer)
		# Testing the trained network
		test(test_loader,model_raw,device,criterion,length)

	# Noisy dataset
	else:
		SNR_dB = list(range(-10,35,5))
		for SNR in SNR_dB:
			train_loader, val_loader, test_loader = get_uav_tdl(algo,dimension,intruder,cond,224,stride,BATCH_SIZE,SNR)
		   	# Training network
			print(f'\nTraining with noisy dataset with SNR={SNR}dB')
			model_noisy = models.vgg16(pretrained=True)
			# Freeze model weights
			for param in model_raw.parameters():
			   param.requires_grad = False

			num_ftrs = model_noisy.classifier[6].in_features
			# Here the size of each output sample is set to 2.
			# Alternatively, it can be generalized to nn.Linear(num_ftrs, len(class_names)).
			model_noisy.classifier[6] = F.softmax(nn.Linear(num_ftrs, 2), dim=1)
			model_noisy.to(device)
			print(model_noisy)
			criterion = nn.BCEWithLogitsLoss()
			optimizer = optim.Adam(model_noisy.parameters(), lr=LEARNING_RATE)
			model_noisy = train(EPOCHS,train_loader,model_noisy,device,criterion,optimizer)
			# Testing the trained network
			test(test_loader,model_noisy,device,criterion,length)
