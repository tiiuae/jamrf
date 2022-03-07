import numpy as np
import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

def rf_classifier(X_train, X_test, y_train, y_test):
    # Training
    rf_model = RandomForestClassifier(n_estimators = 10, random_state = 42)
    rf_model.fit(X_train, y_train)
    # Predicting
    rf_pred = rf_model.predict(X_test)

    # Performance metrics
    rf_acc = accuracy_score(rf_pred,y_test)*100
    return rf_acc

def lr_classifier(X_train, X_test, y_train, y_test):
    # Training
    lr_model = LogisticRegression(random_state=0)
    lr_model.fit(X_train, y_train)

    # Predicting
    lr_pred = lr_model.predict(X_test)

    # # Performance metrics
    lr_acc = accuracy_score(lr_pred,y_test)*100
    return lr_acc
