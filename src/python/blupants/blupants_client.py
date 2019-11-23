import sys
import os
import time
import json
import requests
import socket
import importlib
import blupants.rc_balance_dstr as rc_balance_dstr
import blupants.blupants_car as blupants_car
import threading

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

# TODO refactor this module to be an flask-restful API, so it passivley listen for new code to be executed
# It will allow the BluPants Studio to send code to it directly to the robots via LAN, rather than this module having
# to actively send GET requests for new code


def _reset_rpc_module():
    global dynamic_code_file
    cmd = "echo \"print(\\\"RPC module resetting...\\\")\" > {}".format(dynamic_code_file)
    print(cmd)
    os.system(cmd)
    time.sleep(1)
    import blupants.blupants_rpc
    time.sleep(1)
    dynamic_code_file = os.path.abspath(blupants.blupants_rpc.__file__)
    print(dynamic_code_file)


def _reload_rpc_module(code="print(\"RPC module\")"):
    global dynamic_code_file
    try:
        _reset_rpc_module()
        import blupants.blupants_rpc
        with open(dynamic_code_file, "w") as f:
            f.write(code)
        time.sleep(1)
        module = blupants.blupants_rpc.__name__
        print("Reloading module [{}] from [{}].\nExecuting code: \n\n{}\n\n".format(module, dynamic_code_file, code))
        importlib.reload(sys.modules[module])
    except Exception as ex:
        print(ex)
        _reset_rpc_module()


def execute_python_code(py, version=1):
    global dynamic_code_file
    global step
    itemlist = str(py).split("\n")
    for s in itemlist:
        cmd = str(s)
        if len(cmd) <= 0:
            break

        # TODO: Refactoring - implement an interface and remove all those if robot_id == x statements
        if s == "shutdown()":
            os.system("/usr/bin/rc_test_leds")
            time.sleep(5)
            shutdown()
            time.sleep(5)
            os.system("poweroff")
            return

    if version >= 1:
        dyn_code = "from blupants.blupants_car import *\n"
        if robot_id == 0:
            dyn_code = "from blupants.rc_balance_dstr import *\n"
        dyn_code = dyn_code + py
        _reload_rpc_module(dyn_code)
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
    dyn_code = "from blupants.blupants_car import *\n"
    if robot_id == 0:
        dyn_code = "from blupants.rc_balance_dstr import *\n"
        rc_balance_dstr.shutdown()
    if robot_id == 1:
        blupants_car.shutdown()
    dyn_code = dyn_code + "shutdown()"
    _reload_rpc_module(dyn_code)
    _reset_rpc_module()


def run():
    global robot_id
    global running
    running = True

    if robot_id == 1:
        blupants_car.claw_toggle()
        blupants_car.say_yes()
        blupants_car.claw_toggle()
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

    global buff
    buff = []

    # Test function for panel iframe
    def get_stdout_data():
        global buff

        data = blupants_car.get_stdout()
        if len(data) > 0:
            return data

        time.sleep(1.0)
        if len(buff) >= 6:
            buff = buff[1:]
        buff.append("data:" + str(time.ctime(time.time())))
        data = ""
        for i in buff:
            data += i + "\n"
        return data + "\n"

    # Endpoint to stream stdout data
    @application.route('/stdout_stream')
    def stdout_stream():
        def event_stream():
            while True:
                data = get_stdout_data()
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


