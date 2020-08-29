import sys
import os
import time
import random
import json
import requests
import socket
import threading
import uuid

try:
    import robots_common
except:
    import blupants.robots_common as robots_common

try:
    import robots
except:
    import blupants.robots as robots


global studio_url
studio_url = "http://127.0.0.1:5000"
studio_url = "http://flask-env.6xabhva87h.us-east-2.elasticbeanstalk.com"
studio_url = "http://blupants.org"

global request_counter
request_counter = 0

global public_ip
public_ip = ""

global local_ip
local_ip = "127.0.0.1"

global robot_uuid
robot_uuid = ""

global robot_id
robot_id = 0

global robot_name
robot_name = "BluPants"

global robot_class
robot_class = ""

global dynamic_code_file
dynamic_code_file = "/tmp/blupants/blupants_rpc.py"

global config
config = {}
config_obj = robots_common.RobotConfig()

try:
    config = config_obj.config
except:
    pass

if "robot_id" in config:
    robot_id = config["robot_id"]

if "name" in config:
    robot_name = config["name"]

if robot_id == 0:
    robot_class = "blupants_car"
if robot_id == 1:
    robot_class = "edumip"
if robot_id == 2:
    robot_class = "gripper"
if robot_id == 3:
    robot_class = "ev3"
if robot_id == 4:
    robot_class = "raspberrypi"
if robot_id == 5:
    robot_class = "beagleboneblack"
if robot_id == 6:
    robot_class = "alphabot2"


def _get_pacmd_arg(mem_file):
    pacmd_arg = ""
    with open(mem_file, "r") as f:
        for line in f.readlines():
            if line.lower().find("name: ") != -1:
                tmp = line.split(": ")
                if len(tmp) > 1:
                    arg = tmp[1]
                    arg = arg.replace("\n", "")
                    arg = arg.replace("<", "")
                    arg = arg.replace(">", "")
                    pacmd_arg = arg
                    return pacmd_arg
    return pacmd_arg


def _bluetooth_start():
    global robot_id
    if robot_id != 0 and robot_id != 1:
        return
    try:
        if "bluetooth_addr" in config:
            bluetooth_addr = config["bluetooth_addr"]
            if len(bluetooth_addr) == 0:
                return
            cmd = "echo power on | bluetoothctl"
            os.system(cmd)
            cmd = "echo agent on | bluetoothctl"
            os.system(cmd)
            cmd = "echo default-agent | bluetoothctl"
            os.system(cmd)
            cmd = "echo scan on | bluetoothctl"
            os.system(cmd)

            cmd = "service bluealsa stop"
            os.system(cmd)
            time.sleep(3)
            cmd = "pulseaudio --start"
            os.system(cmd)
            time.sleep(3)

            _bluetooth_connect()
    except:
        pass


def _bluetooth_connect():
    if robot_id != 0 and robot_id != 1:
        return
    try:
        if "bluetooth_addr" in config:
            bluetooth_addr = config["bluetooth_addr"]
            if len(bluetooth_addr) == 0:
                return

            cmd = "echo pair {} | bluetoothctl".format(bluetooth_addr)
            os.system(cmd)
            cmd = "echo trust {} | bluetoothctl".format(bluetooth_addr)
            os.system(cmd)
            cmd = "echo connect {} | bluetoothctl".format(bluetooth_addr)
            os.system(cmd)

            cmd = "pacmd list-cards > /tmp/blupants/cards"
            os.system(cmd)
            time.sleep(1)
            card = _get_pacmd_arg("/tmp/blupants/cards")
            cmd = "pacmd set-card-profile {} a2dp_sink".format(card)
            os.system(cmd)

            cmd = "pacmd list-sinks > /tmp/blupants/sinks"
            os.system(cmd)
            time.sleep(1)
            sink = _get_pacmd_arg("/tmp/blupants/sinks")
            cmd = "pacmd set-default-sink {}".format(sink)
            os.system(cmd)
    except:
        pass


def _create_rpc_content(code="", version=1, quiet=False):
    rpc_code = _create_rpc_file_header(version)
    start_code = "robot.say(\"Initializing code execution!\")\n\n"
    end_code = "\n\nrobot.say(\"Code execution finished!\")\nrobot.shutdown(quiet=True)"
    if quiet:
        start_code = ""
        end_code = "\nrobot.shutdown(quiet=True)"
    rpc_code += start_code + code + end_code
    return rpc_code


def _create_rpc_file_header(version=1):
    header_import = ""
    object_definition = "global robot\nrobot = robots.Robot(\"{}\")\n".format(robot_class)
    dyn_code = header_import + object_definition + "\n\n"
    return dyn_code


def _reset_rpc_module():
    pass


def exec_rpc_code(code="", version=1, quiet=False):
    print("Executing code for robot: [{}]".format(robot_class))
    python_code = _create_rpc_content(code, version, quiet)
    print(python_code)
    try:
        exec(python_code)
    except Exception as ex:
        print(ex)
        try:
            dyn_code = "robot.say(\"ERROR! Check your code syntax.\")\n"
            python_code = _create_rpc_content(dyn_code, version, False)
            exec(python_code)
        except:
            pass
    try:
        with open(dynamic_code_file, "w") as f:
            rpc_headers = "import blupants.robots_common as robots_common\n" \
                          "import blupants.robots as robots\n\n"
            f.write(rpc_headers + python_code)
    except Exception as ex:
        print(ex)


def execute_python_code(py, version=1):
    itemlist = str(py).split("\n")
    for s in itemlist:
        cmd = str(s)
        if len(cmd) <= 0:
            break

        if s == "shutdown()":
            shutdown()
            time.sleep(5)
            os.system("poweroff")
            return

    if version >= 1:
        exec_rpc_code(py, version)
        return


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


def get_public_ip():
    global public_ip
    global request_counter

    request_counter += 1

    if request_counter < 30 and len(public_ip) > 0:
        return public_ip
    else:
        request_counter = 0

    _bluetooth_start()

    url = "https://api.ipify.org/?format=json"
    try:
        resp = requests.get(url=url, timeout=5)
        data = resp.json()
    except:
        return public_ip
    if "ip" in data:
        public_ip = data["ip"]

    return public_ip


def get_code():
    global robot_name
    global robot_uuid
    url = studio_url + "/api/v1/code"
    private_ip = get_local_ip()
    public_ip = get_public_ip()
    params = dict(
        id=private_ip,
        public_ip=public_ip,
        name=robot_name,
        robot_uuid=robot_uuid
    )
    try:
        resp = requests.get(url=url, params=params, timeout=5)
        data = resp.json()
    except:
        data = ""
    if "version" in data and "type" in data and "payload" in data:
        code = data
    else:
        code = {"version": 1, "type": "python", "payload": data}
    return code


def shutdown():
    global running
    running = False
    os.system("touch /tmp/blupants/shutdown")
    _reset_rpc_module()


def run():
    global robot_id
    global robot_uuid
    global running
    running = True
    robot_uuid = uuid.uuid4().hex

    _bluetooth_start()

    dyn_code = "robot.claw_toggle()\n"
    dyn_code += "robot.say_welcome()\n"
    dyn_code += "robot.claw_toggle()\n"
    exec_rpc_code(dyn_code, 1, True)
    _reset_rpc_module()

    while running:
        print("Executing ...")
        code = get_code()
        time.sleep(1)
        if "robot_id" in code:
            robot_id = code["robot_id"]
        version = 1
        if "version" in code:
            version = code["version"]
        if "type" in code:
            if code["type"] == "python":
                payload = {}
                if "payload" in code:
                    payload = code["payload"]
                if bool(payload):
                    execute_python_code(payload, version)
        time.sleep(1)
        print("Done with executing!")

    print("Done!")


def web_server():
    from flask import Flask, Response, render_template

    application = Flask(__name__)
    #application._static_folder = os.path.abspath("templates/static/")

    # Endpoint to stream stdout data
    @application.route('/stdout_stream')
    def stdout_stream():
        def event_stream():
            while True:
                time.sleep(1.0)
                data = robots_common.get_stdout()
                yield "{}".format(data)
        return Response(event_stream(), mimetype="text/event-stream")

    @application.route('/panel')
    def console():
        return render_template('console.html')

    @application.route('/rpc_code')
    def rpc_code():
        global dynamic_code_file
        current_rpc_code = ""
        try:
            with open(dynamic_code_file) as f:
                lines = f.readlines()
                current_rpc_code = "\n".join(lines[7:])
        except:
            return ""
        return current_rpc_code

    application.run(host='0.0.0.0', port="1370", threaded=True)


def main():
    thread1 = threading.Thread(target=run)
    thread2 = threading.Thread(target=web_server)

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()


if __name__ == '__main__':
    main()


