import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn import svm

import kagglehub
import os

# Download latest version
path = 'Internet Speed.csv'
df = pd.read_csv(path)
# print(df)

print('Learning DF')
print(df.columns)


print(df.iloc[0:2,:])

df = df.drop(columns=['Connection_type_DSL', 'Connection_type_Cable', 'Connection_type_Fiber'], axis=1)


df = df.drop(columns=['Router_distance', 'Network_congestion', 'ISP_quality'], axis=1)


df = df.drop(columns=['Weather_conditions'], axis=1)

df['Total_bandwidth'] = df['Download_speed'] + df['Upload_speed']
df['Upload_download_ratio'] = df['Upload_speed'] / df['Download_speed']
df['Network_efficiency'] = df['Download_speed'] / df['Ping_latency']
df['Signal_reliability'] = df['Signal_strength'] / (df['Packet_loss_rate'] + 1)


X = df.drop(columns=['Internet_speed'], axis=1)
Y = df['Internet_speed']


print(Y.describe())

print(df.iloc[100:120, :])


bins = [0, 500, 1000, 2000, 3000, float('inf')]
labels = [0, 1, 2, 3, 4]

df['Internet_class'] = pd.cut(df['Internet_speed'], bins=bins, labels=labels)

print(df[['Internet_speed', 'Internet_class']].head())

Y = df['Internet_class']
X = df.drop(columns=['Internet_class', 'Internet_speed'], axis=1)


X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=2)


sc = StandardScaler()
X_train_scaled = sc.fit_transform(X_train)
X_test_scaled = sc.transform(X_test)

lg = LogisticRegression()
print('Logistictic Regression')
lg.fit(X_train_scaled, Y_train)
X_train_prediction = lg.predict(X_train_scaled)
training_data_accuracy = accuracy_score(X_train_prediction, Y_train)
print('Accuracy score of the training data : ', training_data_accuracy)
X_test_prediction = lg.predict(X_test_scaled)
test_data_accuracy = accuracy_score(X_test_prediction, Y_test)
print('Accuracy score of the test data : ', test_data_accuracy)


svm = svm.SVC()
print('Support Vector Machine')
svm.fit(X_train_scaled, Y_train)
X_train_prediction = svm.predict(X_train_scaled)
training_data_accuracy = accuracy_score(X_train_prediction, Y_train)
print('Accuracy score of the training data : ', training_data_accuracy)
X_test_prediction = svm.predict(X_test_scaled)
test_data_accuracy = accuracy_score(X_test_prediction, Y_test)
print('Accuracy score of the test data : ', test_data_accuracy)

rf = RandomForestClassifier()
print('Random Forest Classifier')
rf.fit(X_train_scaled, Y_train)
X_train_prediction = rf.predict(X_train_scaled)
training_data_accuracy = accuracy_score(X_train_prediction, Y_train)
print('Accuracy score of the training data : ', training_data_accuracy)
X_test_prediction = rf.predict(X_test_scaled)
test_data_accuracy = accuracy_score(X_test_prediction, Y_test)
print('Accuracy score of the test data : ', test_data_accuracy)

xg = XGBClassifier()
print('XGBoost Classifier')
xg.fit(X_train_scaled, Y_train)
X_train_prediction = xg.predict(X_train_scaled)
training_data_accuracy = accuracy_score(X_train_prediction, Y_train)
print('Accuracy score of the training data : ', training_data_accuracy)
X_test_prediction = xg.predict(X_test_scaled)
test_data_accuracy = accuracy_score(X_test_prediction, Y_test)
print('Accuracy score of the test data : ', test_data_accuracy)

print('Enter ping latency : ')
ping_latency = float(input())

print('Enter download speed : ')
download_speed = float(input())

print('Enter upload speed : ')
upload_speed = float(input())

print('Enter signal strength : ')
signal_strength = float(input())

print('Enter packet loss rate : ')
packet_loss_rate = float(input())

# Derived features
bandwidth = download_speed + upload_speed
if download_speed != 0:
  upload_download_ratio = upload_speed / download_speed
else:
  upload_download_ratio = 0
network_efficiency = download_speed / ping_latency
signal_reliability = signal_strength / (packet_loss_rate + 1)

# Create input array (same order as training data)
input_data = np.array([[
    ping_latency,
    download_speed,
    upload_speed,
    packet_loss_rate,
    signal_strength,
    bandwidth,
    upload_download_ratio,
    network_efficiency,
    signal_reliability
]])

# Scale the data
input_scaled = sc.transform(input_data)

# Predictions
lg_pred = lg.predict(input_scaled)
svm_pred = svm.predict(input_scaled)
rf_pred = rf.predict(input_scaled)
xg_pred = xg.predict(input_scaled)
print("Logistic Regression Prediction : ", lg_pred[0])
print("SVM Prediction : ", svm_pred[0])
print("Random Forest Prediction : ", rf_pred[0])
print("XGBoost Prediction : ", xg_pred[0])

predictions = {
    'Logistic Regression': lg_pred[0],
    'SVM': svm_pred[0],
    'Random Forest': rf_pred[0],
    'XGBoost': xg_pred[0]
}

pred_list = list(predictions.values())

final_prediction = max(set(pred_list), key=pred_list.count)

print("Final Predicted Internet Speed Class :", final_prediction)

import joblib

joblib.dump(lg, "lg_model.pkl")
joblib.dump(svm, "svm_model.pkl")
joblib.dump(rf, "rf_model.pkl")
joblib.dump(xg, "xg_model.pkl")
joblib.dump(sc, "scaler.pkl")

print("Models saved successfully!")