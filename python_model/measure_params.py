# import subprocess
# import time
# from ping3 import ping


# # -----------------------------
# # GET SAVED NETWORKS
# # -----------------------------
# def get_saved_networks():

#     result = subprocess.run(
#         ["netsh","wlan","show","profiles"],
#         capture_output=True,
#         text=True
#     )

#     saved = []

#     for line in result.stdout.split("\n"):
#         if "All User Profile" in line:
#             profile = line.split(":")[1].strip()
#             saved.append(profile)

#     return saved


# # -----------------------------
# # GET AVAILABLE NETWORKS
# # -----------------------------
# def get_available_networks():

#     result = subprocess.run(
#         ["netsh","wlan","show","networks"],
#         capture_output=True,
#         text=True
#     )

#     networks = []

#     for line in result.stdout.split("\n"):
#         if "SSID" in line and "BSSID" not in line:
#             name = line.split(":")[1].strip()
#             networks.append(name)

#     return networks


# # -----------------------------
# # CONNECT WIFI
# # -----------------------------
# def connect_wifi(profile):

#     print(f"\nConnecting to {profile}...")

#     subprocess.run(
#         ["netsh","wlan","connect",f"name={profile}"],
#         capture_output=True
#     )

#     time.sleep(8)


# # -----------------------------
# # PING
# # -----------------------------
# def get_ping():

#     latency = ping("8.8.8.8")

#     if latency:
#         return round(latency*1000,2)

#     return None


# # -----------------------------
# # PACKET LOSS
# # -----------------------------
# def get_packet_loss():

#     result = subprocess.run(
#         ["ping","-n","5","8.8.8.8"],
#         capture_output=True,
#         text=True
#     )

#     for line in result.stdout.split("\n"):
#         if "Lost" in line:
#             return line.strip()

#     return None


# # -----------------------------
# # SPEED TEST
# # -----------------------------
# def get_speed():

#     result = subprocess.run(
#         ["speedtest-cli","--simple"],
#         capture_output=True,
#         text=True
#     )

#     return result.stdout


# # -----------------------------
# # MAIN
# # -----------------------------

# print("Scanning nearby networks...\n")

# saved_networks = get_saved_networks()
# available_networks = get_available_networks()

# print("Saved Networks:", saved_networks)
# print("Nearby Networks:", available_networks)

# # Find intersection
# test_networks = [n for n in available_networks if n in saved_networks]

# print("\nNetworks we can test:", test_networks)


# for network in test_networks:

#     try:

#         connect_wifi(network)

#         print(f"\nTesting network: {network}")

#         latency = get_ping()
#         loss = get_packet_loss()
#         speed = get_speed()

#         print("Ping:", latency,"ms")
#         print("Packet Loss:", loss)
#         print(speed)

#         print("\n----------------------------------")

#     except Exception as e:

#         print("Skipping network:", network)
#         print("Reason:", e)

import subprocess
import time
from ping3 import ping
import re


# -----------------------------
# GET SAVED NETWORKS
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
            profile = line.split(":")[1].strip()
            saved.append(profile)

    return saved


# -----------------------------
# GET AVAILABLE NETWORKS
# -----------------------------
def get_available_networks():

    result = subprocess.run(
        ["netsh","wlan","show","networks"],
        capture_output=True,
        text=True
    )

    networks = []

    for line in result.stdout.split("\n"):
        if "SSID" in line and "BSSID" not in line:
            name = line.split(":")[1].strip()
            networks.append(name)

    return networks


# -----------------------------
# CONNECT WIFI
# -----------------------------
def connect_wifi(profile):

    print(f"\nConnecting to {profile}...")

    subprocess.run(
        ["netsh","wlan","connect",f"name={profile}"],
        capture_output=True
    )

    time.sleep(8)


# -----------------------------
# SIGNAL STRENGTH
# -----------------------------
def get_signal():

    result = subprocess.run(
        ["netsh","wlan","show","interfaces"],
        capture_output=True,
        text=True
    )

    for line in result.stdout.split("\n"):
        if "Signal" in line:
            signal = line.split(":")[1].strip()
            signal = signal.replace("%","")
            return int(signal)

    return 0


# -----------------------------
# PING LATENCY
# -----------------------------
def get_ping():

    latency = ping("8.8.8.8")

    if latency:
        return round(latency*1000,2)

    return 0


# -----------------------------
# PACKET LOSS
# -----------------------------
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


# -----------------------------
# SPEED TEST
# -----------------------------
def get_speed():

    download = 0
    upload = 0

    try:

        result = subprocess.run(
            ["speedtest-cli","--simple"],
            capture_output=True,
            text=True
        )

        output = result.stdout

        for line in output.split("\n"):

            if "Download" in line:
                download = float(line.split()[1])

            if "Upload" in line:
                upload = float(line.split()[1])

    except:
        pass

    return download, upload


# -----------------------------
# MAIN
# -----------------------------

print("Scanning nearby networks...\n")

saved_networks = get_saved_networks()
available_networks = get_available_networks()

test_networks = [n for n in available_networks if n in saved_networks]

print("Networks we can test:", test_networks)


for network in test_networks:

    try:

        connect_wifi(network)

        print(f"\nTesting network: {network}")

        latency = get_ping()
        signal = get_signal()
        packet_loss = get_packet_loss()
        download, upload = get_speed()

        print("Ping Latency:", latency,"ms")
        print("Signal Strength:", signal,"%")
        print("Download Speed:", download,"Mbps")
        print("Upload Speed:", upload,"Mbps")
        print("Packet Loss:", packet_loss,"%")

        print("\n----------------------------------")

    except Exception as e:

        print("Skipping network:", network)
        print("Reason:", e)