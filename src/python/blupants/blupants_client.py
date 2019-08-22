import os
import time
import cv2
import threading
import requests
import socket
import json
import blupants.rc_balance_dstr as rc_balance_dstr
import blupants.blupants_car as blupants_car

global studio_url
studio_url = "http://flask-env.6xabhva87h.us-east-2.elasticbeanstalk.com"
studio_url = "http://blupants.org"

global local_ip
local_ip = "127.0.0.1"

global robot_id
robot_id = 0  # mr_blupants / eduMIP
robot_id = 1  # blupants_car

global step
step = 1


# TODO refactor this module to be an flask-restful API, so it passivley listen for new code to be executed
# It will allow the BluPants Studio to send code to it directly to the robots via LAN, rather than this module having
# to actively send GET requests for new code

def execute_python_code(py):
    global step
    itemlist = str(py).split("\n")
    for s in itemlist:
        cmd = str(s)
        if len(cmd) <= 0:
            break

        # TODO: Refactoring - implement an interface and remove all those if robot_id == x statements
        if s == "claw()" or s == "claw_toggle()" or s == "claw_open()" or s == "claw_close()":
            if robot_id == 0:
                rc_balance_dstr.claw_toggle()
            if robot_id == 1:
                blupants_car.claw_toggle()
        if s == "shutdown()":
            os.system("/usr/bin/rc_test_leds")
            time.sleep(5)
            shutdown()
            time.sleep(5)
            os.system("poweroff")
        if s == "move_forward()":
            if robot_id == 0:
                rc_balance_dstr.move_block(step)
            if robot_id == 1:
                blupants_car.forward(step)
        if s == "move_backwards()" or s == "move_backwards":
            if robot_id == 0:
                rc_balance_dstr.move_block(step*-1)
            if robot_id == 1:
                blupants_car.backward(step)
        if s == "speed_up()":
            step += 1
            if robot_id == 0:
                rc_balance_dstr.move_block(step)
            if robot_id == 1:
                blupants_car.forward(step)
        if s == "turn_left()":
            if robot_id == 0:
                rc_balance_dstr.turn_left(90.0)
            if robot_id == 1:
                blupants_car.turn_left(90.0)
        if s == "turn_right()":
            if robot_id == 0:
                rc_balance_dstr.turn_right(90.0)
            if robot_id == 1:
                blupants_car.turn_right(90.0)
        if s == "turn_left(45)":
            if robot_id == 0:
                rc_balance_dstr.turn_left(45.0)
            if robot_id == 1:
                blupants_car.turn_left(45.0)
        if s == "turn_right(45)":
            if robot_id == 0:
                rc_balance_dstr.turn_right(45.0)
            if robot_id == 1:
                blupants_car.turn_right(45.0)
        if s == "turn_left(180)":
            if robot_id == 0:
                rc_balance_dstr.turn_left(180.0)
            if robot_id == 1:
                blupants_car.turn_left(180.0)
        if s == "turn_right(180)":
            if robot_id == 0:
                rc_balance_dstr.turn_right(180.0)
            if robot_id == 1:
                blupants_car.turn_right(180.0)


def get_local_ip():
    global local_ip
    if local_ip != "127.0.0.1":
        return local_ip
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        local_ip = s.getsockname()[0]
    except:
        local_ip = "127.0.0.1"
    finally:
        s.close()
    return local_ip


def get_code():
    url = studio_url + "/api/v1/code"
    private_ip = get_local_ip()
    params = dict(
        id=private_ip
    )
    try:
        resp = requests.get(url=url, params=params, timeout=5)
        data = resp.json()
    except:
        data = ""
    # TODO change server to send the code type
    code = {"type": "python", "code": data}
    return code


def shutdown():
    global running
    running = False
    if robot_id == 0:
        rc_balance_dstr.shutdown()
    if robot_id == 1:
        blupants_car.shutdown()


def _set_wifi(ssid, pw, tries=5):
    tmp_wifi_file = "/tmp/blupants_wifi"
    ap_id = ""
    ssid_found = False
    counter = 0
    while not ssid_found:
        cmd = "connmanctl services > {}".format(tmp_wifi_file)
        os.system(cmd)
        time.sleep(5)
        counter += 1
        with open(tmp_wifi_file) as f:
            for line in f.readlines():
                line = line.replace("  ", " ")
                line = line.strip()
                tmp = line.split(" ")
                if len(tmp) > 1:
                    line_ssid = tmp[0]
                    if line_ssid.lower() == ssid.lower():
                        ssid_found = True
                        ssid = tmp[0]
                        ap_id = tmp[-1]
                        break
        time.sleep(1)
        if counter >= tries:
            break
    wifi_config_file = "/var/lib/connman/{}-psk.config".format(ssid)
    with open(wifi_config_file, "w") as f:
        lines = "[service_{}]\n".format(ap_id)
        lines += "Type = wifi\n"
        lines += "Name = {}\n".format(ssid)
        lines += "Passphrase = {}".format(pw)
        f.write(lines)
        time.sleep(2)

    cmd = "connmanctl connect {}".format(ap_id)
    os.system(cmd)
    time.sleep(5)

    ip = get_local_ip()
    return str(ip).lower() == "127.0.0.1"


def set_config(config_data):
    resp = False
    ssid = ""
    pw = ""
    if "ssid" in config_data:
        ssid = config_data["ssid"]
    if "pw" in config_data:
        pw = config_data["pw"]
    try:
        resp = _set_wifi(ssid, pw)
        if resp:
            blupants_car.say_yes()
    except:
        resp = False
    if not resp:
        blupants_car.say_no()
    return resp


def process_video(video_source=0):
    global running

    qr_decoder = cv2.QRCodeDetector()
    cap = cv2.VideoCapture(video_source)
    # Check if camera opened successfully
    if not cap.isOpened():
        print("Error opening video stream or file")

    # Read until video is completed
    while cap.isOpened():
        # Capture frame-by-frame
        ret, frame = cap.read()
        if ret:
            data, bbox, rectified_image = qr_decoder.detectAndDecode(frame)
            if len(data) > 0:
                print("Decoded Data : {}".format(data))
                data = json.loads(data)
                if "ssid" in data:
                    set_config(data)
            else:
                print("QR Code not detected")

        else:
            break

        if not running:
            break

def run():
    global running
    running = True

    # run opencv in a separate thread
    thread = threading.Thread(target=process_video())
    thread.start()

    while running:
        print("Executing ...")
        code = get_code()
        time.sleep(1)
        if "type" in code:
            if code["type"] == "python":
                if "code" in code:
                    execute_python_code(code["code"])
        time.sleep(1)
        print("Done with executing!")

    thread.join()
    print("Done!")



def main():
    return run()


if __name__ == '__main__':
    main()


