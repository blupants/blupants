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
except Exception as e:
    print(e.message)

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
    exec(python_code)
    try:
        with open(dynamic_code_file, "w") as f:
            rpc_headers = "import blupants.robots_common as robots_common\n" \
                          "import blupants.robots as robots\n\n"
            f.write(rpc_headers + python_code)
    except:
        pass


def execute_python_code(py, version=1):
    itemlist = str(py).split("\n")
    for s in itemlist:
        cmd = str(s)
        if len(cmd) <= 0:
            break

        # TODO: Refactoring - implement an interface and remove all those if robot_id == x statements
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


def get_code():
    global robot_name
    global robot_uuid
    url = studio_url + "/api/v1/code"
    private_ip = get_local_ip()
    params = dict(
        id=private_ip,
        name=robot_name,
        robot_uuid=robot_uuid
    )
    try:
        resp = requests.get(url=url, params=params, timeout=5)
        data = resp.json()
    except:
        data = ""
    # TODO change server to send the code type
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
        except Exception as ex:
            print(ex.message)
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


