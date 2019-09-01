import os
import time
import cv2
import requests

global studio_url
studio_url = "http://blupants.org"


def wifi_connected():
    global studio_url
    url = studio_url + "/api/v1/status"
    try:
        resp = requests.get(url=url, timeout=5)
        if resp.status_code == 200:
            return True
    except:
        return False
    return False


def _set_wifi(ssid, pw, tries=5):
    tmp_wifi_file = "/tmp/blupants_wifi"
    ap_id = ""
    ssid_found = False
    counter = 0
    cmd = "connmanctl scan wifi"
    print(cmd)
    os.system(cmd)
    time.sleep(5)
    while not ssid_found:
        cmd = "connmanctl services > {}".format(tmp_wifi_file)
        print(cmd)
        os.system(cmd)
        time.sleep(2)
        counter += 1
        with open(tmp_wifi_file) as f:
            for line in f.readlines():
                ssid_index = 0
                if not line.startswith(" "):
                    ssid_index = 1
                line = line.replace("  ", " ")
                line = line.strip()
                tmp = line.split(" ")
                if len(tmp) > 1:
                    line_ssid = tmp[ssid_index]
                    if line_ssid.lower() == ssid.lower():
                        ssid_found = True
                        ssid = tmp[ssid_index]
                        ap_id = tmp[-1]
                        break
        time.sleep(1)
        if counter >= tries:
            break
    wifi_config_file = "/var/lib/connman/{}-psk.config".format(ssid)
    print(wifi_config_file)
    with open(wifi_config_file, "w") as f:
        lines = "[service_{}]\n".format(ap_id)
        lines += "Type = wifi\n"
        lines += "Name = {}\n".format(ssid)
        lines += "Passphrase = {}".format(pw)
        f.write(lines)
        time.sleep(2)
        print(lines)

    cmd = "connmanctl connect {}".format(ap_id)
    print(cmd)
    os.system(cmd)
    time.sleep(5)


def set_config(config_data):
    # WIFI:S:BluPantslab;T:WPA;P:s3cr3t@123;;
    resp = False
    ssid = ""
    pw = ""
    if len(config_data) > 0:
        fields = config_data.split(";")
        if len(fields) > 2:
            wifi = fields[0]
            enc = fields[1]
            password = fields[2]
            wifi_fields = wifi.split(":")
            if len(wifi_fields) > 2:
                ssid = wifi_fields[2]
            password_fields = password.split(":")
            if len(password_fields) > 1:
                pw = password_fields[1]
    try:
        resp = _set_wifi(ssid, pw)
    except:
        resp = False
    return resp


def run(max_tries=-1):
    if wifi_connected():
        print("It is connected to WiFi already.")
        return
    file_motion = "/tmp/motion/pic.jpg"
    file_qr = "/tmp/motion/pic_opencv.jpg"
    qr_decoder = cv2.QRCodeDetector()
    cmd = "mkdir -p /tmp/motion/"
    os.system(cmd)
    counter  = 0
    while True:
        counter += 1
        print("Trying to connect to Wifi vi QR Code ... Attempt [{}/{}]".format(counter, max_tries))
        cmd = "cp %s %s" % (file_motion, file_qr)
        os.system(cmd)
        time.sleep(1)
        cap = cv2.VideoCapture(file_qr)
        time.sleep(1)
        # Capture frame-by-frame
        ret, frame = cap.read()
        if ret:
            data, bbox, rectifiedImage = qr_decoder.detectAndDecode(frame)
            if len(data) > 0:
                print("Decoded Data : {}".format(data))
                set_config(data)
            else:
                print("QR Code not detected")
        if 0 < max_tries <= counter:
            print("Unable to connected to WiFi.")
            cap.release()
            break
        if wifi_connected():
            print("Successfully connected to WiFi.")
            cap.release()
            break

    print("Done!")
    return


def main():
    return run()


if __name__ == '__main__':
    main()


