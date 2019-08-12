import os
import time

# TODO this is a temporary workaround while we can't get pyctrl module to work: https://github.com/mcdeoliveira/pyctrl
# This module will br replaced the edumip.py

"""
This packaged depends on a modified version of the original rc_balance. You will need to modify the
original rc_balance.c and recompile it to make it work. Please follow the instructions below:

https://github.com/StrawsonDesign/librobotcontrol
wget https://raw.githubusercontent.com/blupants/blupants/master/rc_balance.c -O rc_balance.c
git clone https://github.com/StrawsonDesign/librobotcontrol.git
cp ./librobotcontrol/examples/src/rc_balance.c ./librobotcontrol/examples/src/rc_balance.c.ORIGINAL
cp ./rc_balance.c ./librobotcontrol/examples/src/rc_balance.c
cd librobotcontrol
make
cp ./examples/bin/rc_balance /usr/bin/rc_balance_dstr
rc_balance_dstr -i dstr
"""


global turn_coefficient
turn_coefficient = 0.0175

global meter_coefficient
meter_coefficient = 14


global var_dir
var_dir = os.path.join(os.sep, "tmp")


print("Make sure you have eduMPI balanced before running this script.")
print("#rc_balance_dstr -i dstr")


def _create_cmd_file(cmd):
    global var_dir
    file_path = os.path.join(var_dir, cmd)
    open(file_path, 'a').close()


def move_forward(distance_meter = 1.0):
    global meter_coefficient
    print ("Moving forward")
    _create_cmd_file("up.txt.")
    time.sleep(meter_coefficient*distance_meter)
    _create_cmd_file("break.txt.")
    time.sleep(2)


def move_back(distance_meter = 1.0):
    global meter_coefficient
    print("Moving back")
    _create_cmd_file("down.txt.")
    time.sleep(meter_coefficient*distance_meter)
    _create_cmd_file("break.txt.")
    time.sleep(2)


def turn_left(degree = 90.0):
    global turn_coefficient
    print("Turning left")
    _create_cmd_file("left.txt.")
    time.sleep(turn_coefficient*degree)
    _create_cmd_file("break.txt.")
    time.sleep(2)


def turn_right(degree = 90.0):
    global turn_coefficient
    print("Turning right")
    _create_cmd_file("right.txt.")
    time.sleep(turn_coefficient*degree)
    _create_cmd_file("break.txt.")
    time.sleep(2)


def move_block(blocks=1):
    block_size_meters = 0.28
    if blocks > 0:
        move_forward(block_size_meters * blocks)
    else:
        move_back(block_size_meters * (blocks * -1))


def spin_360():
    turn_left()
    turn_left()
    turn_left()
    turn_left()


def kitcken_lap():
    move_forward(1.2)
    turn_left()
    move_forward(2.1)
    turn_left()
    move_forward(1.2)
    turn_left()
    move_forward(2.1)
    turn_left()


def shutdown():
    global running
    running = False


