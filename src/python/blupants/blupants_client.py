import sys
import os
import time
import json
import requests
import socket
import threading

try:
    import robots_common
except:
    import blupants.robots_common as robots_common

global studio_url
studio_url = "http://flask-env.6xabhva87h.us-east-2.elasticbeanstalk.com"
studio_url = "http://blupants.org"

global local_ip
local_ip = "127.0.0.1"

global robot_id
robot_id = 0  # blupants_car
# robot_id = 1  # mr_blupants / eduMIP
# robot_id = 2  # gripper

global robot_name
robot_name = ""

global dynamic_code_file
dynamic_code_file = "/usr/local/lib/python3.5/dist-packages/blupants/blupants_rpc.py"


global config_file
config_file = "/root/blupants.json"

global config
config = {}

if os.path.isfile(config_file):
    with open(config_file) as f:
        config = json.load(f)
        print(config)

if "robot_id" in config:
    robot_id = config["robot_id"]

if robot_id == 0:
    robot_name = "blupants_car"
if robot_id == 1:
    robot_name = "edumip"
if robot_id == 2:
    robot_name = "gripper"
if robot_id == 3:
    robot_name = "ev3"

# TODO refactor this module to be an flask-restful API, so it passivley listen for new code to be executed
# It will allow the BluPants Studio to send code to it directly to the robots via LAN, rather than this module having
# to actively send GET requests for new code


def _create_rpc_content(code=""):
    rpc_code = _create_rpc_file_header()
    rpc_code += code
    rpc_code += "\n\nshutdown(quiet=True)"
    return rpc_code


def _create_rpc_file_header():
    print("Executing code for robot: [{}]".format(robot_name))
    header_import = "\
try:\n\
  import robots\n\
except:\n\
  import blupants.robots as robots\n\
"
    object_definition = "robot = robots.Robot(\"{}\")\n".format(robot_name)
    functions = ""
    try:
        for func in dir(robots_common.RobotHollow):
            line = "{} = robot.{}\n".format(func, func)
            if not line.startswith("_"):
                functions += line
    except:
        for func in dir(blupants.robots_common.RobotHollow):
            line = "{} = robot.{}\n".format(func, func)
            if not line.startswith("_"):
                functions += line
    dyn_code = header_import + object_definition + functions
    return dyn_code


def _reset_rpc_module():
    global dynamic_code_file
    cmd = "echo \"print(\\\"RPC module resetting...\\\")\" > {}".format(dynamic_code_file)
    os.system(cmd)
    time.sleep(1)


def _exec_rpc_code(code=""):
    global dynamic_code_file
    python_code = _create_rpc_content(code)
    with open(dynamic_code_file, "w") as f:
        f.write(python_code)
    time.sleep(1)
    os.system("python3 {}".format(dynamic_code_file))
    return


def execute_python_code(py, version=1):
    global dynamic_code_file
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
        _exec_rpc_code(py)
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
    if "version" in data and "type" in data and "payload" in data:
        code = data
    else:
        code = {"version": 1, "type": "python", "payload": data}
    return code


def shutdown():
    global running
    running = False
    _reset_rpc_module()


def run():
    global robot_id
    global running
    running = True

    dyn_code = "claw_toggle()\n"
    dyn_code += "say_welcome()\n"
    dyn_code += "claw_toggle()\n"
    _exec_rpc_code(dyn_code)
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


