from flask import Flask, jsonify, request
import subprocess
import time
import re
import numpy as np
import joblib
from ping3 import ping

app = Flask(__name__)

# -----------------------------
# LOAD ML MODELS
# -----------------------------
lg = joblib.load("lg_model.pkl")
svm = joblib.load("svm_model.pkl")
rf = joblib.load("rf_model.pkl")
xg = joblib.load("xg_model.pkl")
scaler = joblib.load("scaler.pkl")


# -----------------------------
# WIFI FUNCTIONS
# -----------------------------

def get_saved_networks():

    result = subprocess.run(
        ["netsh","wlan","show","profiles"],
        capture_output=True,
        text=True
    )

    saved = []

    for line in result.stdout.split("\n"):
        if "All User Profile" in line:
            saved.append(line.split(":")[1].strip())

    return saved


def get_available_networks():

    result = subprocess.run(
        ["netsh","wlan","show","networks"],
        capture_output=True,
        text=True
    )

    networks = []

    for line in result.stdout.split("\n"):
        if "SSID" in line and "BSSID" not in line:
            networks.append(line.split(":")[1].strip())

    return networks


def connect_wifi(profile):

    subprocess.run(
        ["netsh","wlan","connect",f"name={profile}"],
        capture_output=True
    )

    time.sleep(6)


def get_signal():

    result = subprocess.run(
        ["netsh","wlan","show","interfaces"],
        capture_output=True,
        text=True
    )

    for line in result.stdout.split("\n"):
        if "Signal" in line:
            signal = line.split(":")[1].strip()
            return int(signal.replace("%",""))

    return 0


def get_ping():

    latency = ping("8.8.8.8")

    if latency:
        return round(latency*1000,2)

    return 0


def get_packet_loss():

    result = subprocess.run(
        ["ping","-n","5","8.8.8.8"],
        capture_output=True,
        text=True
    )

    for line in result.stdout.split("\n"):

        if "Lost" in line:

            match = re.search(r"\((\d+)% loss\)", line)

            if match:
                return int(match.group(1))

    return 0


def get_speed():

    download = 0
    upload = 0

    result = subprocess.run(
        ["speedtest-cli","--simple"],
        capture_output=True,
        text=True
    )

    for line in result.stdout.split("\n"):

        if "Download" in line:
            download = float(line.split()[1])

        if "Upload" in line:
            upload = float(line.split()[1])

    return download, upload


# -----------------------------
# GET API
# -----------------------------
@app.route("/scan", methods=["GET"])

def scan():

    saved = get_saved_networks()
    available = get_available_networks()

    test_networks = [n for n in available if n in saved]

    networks_data = []

    for net in test_networks:

        try:

            connect_wifi(net)

            latency = get_ping()
            signal = get_signal()
            packet_loss = get_packet_loss()
            download, upload = get_speed()

            networks_data.append({

                "network_name": net,
                "ping_latency": latency,
                "signal_strength": signal,
                "download_speed": download,
                "upload_speed": upload,
                "packet_loss_rate": packet_loss

            })

        except:
            pass

    return jsonify({"networks": networks_data})


# -----------------------------
# POST API (ML Prediction)
# -----------------------------
@app.route("/predict", methods=["POST"])

def predict():

    data = request.json

    networks = data["networks"]

    available_networks = []
    network_strength = []
    network_probability = []

    for net in networks:

        name = net["network_name"]

        ping_latency = net["ping_latency"]
        download_speed = net["download_speed"]
        upload_speed = net["upload_speed"]
        signal_strength = net["signal_strength"]
        packet_loss_rate = net["packet_loss_rate"]

        bandwidth = download_speed + upload_speed
        upload_download_ratio = upload_speed / download_speed if download_speed != 0 else 0
        network_efficiency = download_speed / ping_latency if ping_latency != 0 else 0
        signal_reliability = signal_strength / (packet_loss_rate + 1)

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

        input_scaled = scaler.transform(input_data)

        lg_pred = lg.predict(input_scaled)[0]
        svm_pred = svm.predict(input_scaled)[0]
        rf_pred = rf.predict(input_scaled)[0]
        xg_pred = xg.predict(input_scaled)[0]

        preds = [lg_pred, svm_pred, rf_pred, xg_pred]

        final_prediction = max(set(preds), key=preds.count)

        probability = preds.count(final_prediction) / 4

        available_networks.append(name)
        network_strength.append(int(final_prediction))
        network_probability.append(probability)

    return jsonify({

        "available_networks": available_networks,
        "network_strength": network_strength,
        "network_probability_class": network_probability

    })


if __name__ == "__main__":
    app.run(debug=True)