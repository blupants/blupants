import time
import rcpy.motor as motor
from rcpy.motor import motor2
from rcpy.motor import motor3

global duty
duty = 0.8


# TODO get the pyctrl module to work: https://github.com/mcdeoliveira/pyctrl
# This module will replace the rc_balance_dstr.py, and the need to modify rc_balance.c

def move_back(distance_meters = 1):
    global duty
    if duty > 0:
        duty = duty * -1
    move_distance(distance_meters)


def move_forward(distance_meters = 1):
    global duty
    if duty < 0:
        duty = duty * -1
    move_distance(distance_meters)


def move_distance(distance_meters = 1):
    global duty
    motor_left = motor2
    motor_right = motor3

    motor_left.set(duty * 0.5)
    motor_right.set(-duty * 0.5)
    time.sleep(1.35*distance_meters)
    motor_left.set(0)
    motor_right.set(0)
    time.sleep(1)


def turn_right():
    global duty
    if duty < 0:
        duty = duty * -1
    motor_right = motor3
    turn(motor_right)


def turn_left():
    global duty
    if duty > 0:
        duty = duty * -1
    motor_left = motor3
    turn(motor_left)


def turn(motor):
    global duty
    motor.set(duty * 0.5)
    time.sleep(0.3)
    motor.set(0)
    time.sleep(1)


def test(dist = 1):
    move_forward(dist)
    turn_right()
    turn_right()
    move_forward(dist)
    turn_left()
    turn_left()
    move_forward(dist)
    turn_left()
    turn_left()
    move_forward(dist)
    turn_left()
    turn_left()
    move_forward(dist)
    turn_right()
    turn_right()
    turn_right()
    turn_right()
    move_back(dist)

