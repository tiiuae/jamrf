#!/usr/bin/env python
# coding:utf-8
"""
name        : main.py,
version     : 1.0.0,
url         : https://github.com/abubakar-sani/RFF,
license     : MIT License,
copyright   : Copyright 2021 by Abubakar Sani Ali, Khalifa University,
author      : Abubakar Sani Ali,
email       : engrabubakarsani@gmail.com,
date        : 9/5/2021,
description : Machine Learning classifiers for RFF,
"""

#%% Loading libraries

import itertools
import numpy as np
import matplotlib.pyplot as plt

def plot_confusion_matrix(cm, classes, results_dir, dist, normalize=False, title='Confusion matrix', cmap=plt.cm.Blues):
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    print(cm)
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, format(cm[i, j], fmt), horizontalalignment="center", color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    name = f'{results_dir}/ORACLEconfusion_matrix_{dist}ft.png'
    plt.savefig(name)
