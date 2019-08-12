import os
import time
import requests
import socket
import blupants.blupants_car as rc_balance_dstr
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
        if s == "move_forward()":
            if robot_id == 0:
                rc_balance_dstr.move_block(step)
            if robot_id == 1:
                blupants_car.forward(step)
        if s == "move_backwards":
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


def run():
    global running
    running = True
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
    print("Done!")


def main():
    return run()


if __name__ == '__main__':
    main()


