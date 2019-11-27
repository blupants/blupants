import os
import json
import rcpy
import rcpy.motor as motor
import rcpy.servo as servo
import rcpy.clock as clock
import rcpy.gpio as gpio
from rcpy.gpio import InputEvent
import Adafruit_BBIO.GPIO as GPIO

import time
import random

global grab
grab = True

global config_file
config_file = "/root/blupants.json"

global config


class BluPantsConsole:
    def __init__(self):
        self.buffer = []

    def get_stdout(self):
        data = ""
        for message in self.buffer:
            data += message + "\n"
        return data + "\n"

    def print(self, message):
        print(message)
        if len(self.buffer) >= 6:
            self.buffer = self.buffer[1:]
        self.buffer.append("data:" + str(message))

global standard_output
standard_output = BluPantsConsole()


GPIO.cleanup()

config = {}
if os.path.isfile(config_file):
    with open(config_file) as f:
        config = json.load(f)
        print(config)

duty = 0.3
interval = 2
period = 0.02
turn_left_calibrate = 0.0052
turn_right_calibrate = 0.0053
duty_lr_ratio = 1.0
if "blupants_car" in config:
    if "duty" in config["blupants_car"]:
        duty = config["blupants_car"]["duty"]
    if "duty_lr_ratio" in config["blupants_car"]:
        duty_lr_ratio = config["blupants_car"]["duty_lr_ratio"]
    if "interval" in config["blupants_car"]:
        interval = config["blupants_car"]["interval"]
    if "period" in config["blupants_car"]:
        period = config["blupants_car"]["period"]
    if "turn_left_calibrate" in config["blupants_car"]:
        turn_left_calibrate = config["blupants_car"]["turn_left_calibrate"]
    if "turn_right_calibrate" in config["blupants_car"]:
        turn_right_calibrate = config["blupants_car"]["turn_right_calibrate"]


#0
#unused
#1
#unused
#2
echo = "P9_23" #echo = "GPIO1_17" # resitor yellow
#3
trigger = "GPIO1_25"  # direct white
#4
vcc = "GP0_3v3"       # direct blue
#5
gnd = "GP0_GND"       # direct green


GPIO.cleanup()


#Configuration
print("trigger: [{}]".format(trigger))
GPIO.setup(trigger,GPIO.OUT) #Trigger
print("echo: [{}]".format(echo))
GPIO.setup(echo,GPIO.IN)  #Echo
GPIO.output(trigger, False)
print("Setup completed!")

#Security
GPIO.output(trigger, False)
time.sleep(0.5)
TRIG = trigger


motor1 = motor.Motor(1) # Left
motor2 = motor.Motor(2) # Right
motor3 = motor.Motor(3)
motor4 = motor.Motor(4)


blupants_servos = [servo.Servo(1), servo.Servo(2), servo.Servo(3), servo.Servo(4), servo.Servo(5), servo.Servo(6),
                   servo.Servo(7), servo.Servo(8)]

clcks = [clock.Clock(blupants_servos[0], period), clock.Clock(blupants_servos[1], period),
         clock.Clock(blupants_servos[2], period), clock.Clock(blupants_servos[3], period),
         clock.Clock(blupants_servos[4], period), clock.Clock(blupants_servos[5], period),
         clock.Clock(blupants_servos[6], period), clock.Clock(blupants_servos[7], period)]


rcpy.set_state(rcpy.RUNNING)
# enable servos
servo.enable()


for i in range(0, 8):
    clcks[i].start()


def get_stdout():
    global standard_output
    return standard_output.get_stdout()


def print_stdout(message):
    global standard_output
    standard_output.print(message)


global camera_pos
camera_pos = 0
camera_toggle_postions = [[-89.0, 0], [89.0, 0],
                          [89.0, 30.0], [0, 30.0], [-89.0, 30.0],
                          [-89.0, 0],
                          [-89.0, -30.0], [0, -30.0], [89.0, -30.0],
                          [89.0, 0], [0, 0]]


def camera_toggle():
    global camera_pos
    max = len(camera_toggle_postions)
    if camera_pos >= max:
        camera_pos = 0
    pos = camera_toggle_postions[camera_pos]
    time.sleep(0.2)
    set_servo(1, pos[0])
    time.sleep(0.2)
    set_servo(2, pos[1])
    time.sleep(0.2)
    camera_pos += 1


def sleep(seconds=1.0):
    global standard_output
    message = "sleep(seconds={})".format(seconds)
    standard_output.print(message)
    time.sleep(seconds)


def read_distance():
    distance = distanceMeasurement(trigger, echo)
    print_stdout("Distance: [{}] cm.".format(str(distance)))
    return distance


def move_forward(step=1):
    return forward(step)


def move_backwards(step=1):
    return backward(step)


def set_motor(i=1, duty=0.5):
    print_stdout("set_motor(i={}, duty={})".format(i, duty))
    if i == 1:
        motor1.set(duty)
    if i == 2:
        motor2.set(duty)
    if i == 3:
        motor3.set(duty)
    if i == 4:
        motor4.set(duty)


def set_servo(i=1, angle=0):
    print_stdout("set_servo({}, {})".format(i, angle))
    time.sleep(0.2)
    if angle > 0 and angle > 90:
        angle = 90
    if angle < 0 and angle < -90:
        angle = -90
    position = angle * 0.015
    blupants_servos[i-1].set(position)
    time.sleep(0.2)


def claw_toggle():
    global grab
    if grab:
        claw_close()
    else:
        claw_open()


def claw():
    return claw_toggle()


def claw_open():
    global grab
    print_stdout("release()")
    grab = True
    angle = -89.00
    time.sleep(0.2)
    position = angle * 0.015
    blupants_servos[7].set(position)
    time.sleep(0.2)


def claw_close():
    global grab
    print_stdout("grab()")
    grab = False
    angle = 89.0
    time.sleep(0.2)
    position = angle * 0.015
    blupants_servos[7].set(position)
    time.sleep(0.2)


def distanceMeasurement(TRIG,ECHO):
    max = 10000
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)
    pulse_start = time.time()
    pulse_end = time.time()
    counter = 0
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
        counter += 1
        if counter > max:
            return -1
    counter = 0
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()
        counter += 1
        if counter > max:
            return -1

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)
    return distance


def look_back():
    print_stdout("look_back()")
    blupants_servos[1].set(-1.5)
    time.sleep(0.2)


def look_angle(angle=90):
    print_stdout("look_angle({})".format(angle))
    time.sleep(0.2)
    if angle > 0 and angle > 90:
        angle = 90
    if angle < 0 and angle < -90:
        angle = -90
    position = angle * 0.015
    blupants_servos[0].set(position)
    blupants_servos[1].set(0)
    time.sleep(0.2)


def say_yes():
    print_stdout("say_yes()")
    blupants_servos[1].set(0)
    time.sleep(0.2)
    blupants_servos[1].set(1.5)
    time.sleep(0.2)
    blupants_servos[1].set(-1.5)
    time.sleep(0.2)
    blupants_servos[1].set(1.5)
    time.sleep(0.2)
    blupants_servos[1].set(0)
    time.sleep(0.2)


def say_no():
    print_stdout("say_no()")
    blupants_servos[1].set(0)
    time.sleep(0.2)
    blupants_servos[0].set(0)
    time.sleep(0.4)
    blupants_servos[0].set(1.5)
    time.sleep(0.2)
    blupants_servos[0].set(-1.4)
    time.sleep(0.4)
    blupants_servos[0].set(0)
    time.sleep(0.2)
    look_angle(0)


def move_block(blocks):
    d = duty
    if blocks < 0:
        d = d * -1
        blocks = blocks * -1

    motor1.set(d * duty_lr_ratio)
    motor2.set(d)
    motor3.set(d)
    motor4.set(d * duty_lr_ratio)

    time.sleep(interval * blocks)

    motor1.set(0)
    motor2.set(0)
    motor3.set(0)
    motor4.set(0)


def turn_right(angle=90):
    print_stdout("turn_right({})".format(angle))
    motor1.set(duty)
    motor2.set(duty*-1)
    motor3.set(duty*-1)
    motor4.set(duty)
    time.sleep(turn_right_calibrate * angle)
    motor1.set(0)
    motor2.set(0)
    motor3.set(0)
    motor4.set(0)


def turn_left(angle=90):
    print_stdout("turn_left({})".format(angle))
    motor1.set(duty*-1)
    motor2.set(duty)
    motor3.set(duty)
    motor4.set(duty*-1)
    time.sleep(turn_left_calibrate * angle)
    motor1.set(0)
    motor2.set(0)
    motor3.set(0)
    motor4.set(0)


def forward(blocks=1):
    print_stdout("forward({})".format(blocks))
    return move_block(blocks)


def backward(blocks=1):
    print_stdout("backward({})".format(blocks))
    return forward(-blocks)


def random_move(force=False):
    rand = random.randint(0, 100)
    if force or rand < 25:
        rand = random.randint(15, 180)
        print("random_move({}) step1".format(str(rand)))
        look_back()
        left = bool(random.getrandbits(1))
        if left:
            turn_left(rand)
        else:
            turn_right(rand)
        backward()
        print("random_move({}) step2".format(str(rand)))
        left = not left
        if left:
            turn_left(rand)
        else:
            turn_right(rand)


def shutdown():
    global running
    print_stdout("shutdown()")
    running = False
    # stop clock
    for i in range(0, 8):
        clcks[i].stop()

    # disable servos
    servo.disable()


def main():
    global running
    running = True
    print("Init")

    recovered_distance = distanceMeasurement(trigger, echo)
    while running:
        #  TODO: implement stop condition to break the loop and execute the stop commands at the end
        if recovered_distance <= 0 or recovered_distance > 400:
            recovered_distance = 1.111
        while recovered_distance > 80.0:
            print("Distance: [{}] cm. Clear path!".format((str(recovered_distance))))
            say_yes()
            forward()
            time.sleep(1)
            recovered_distance = distanceMeasurement(trigger, echo)
            if recovered_distance <= 0 or recovered_distance > 400:
                recovered_distance = 1.111
            random_move()
        # Found obstacle
        print("Distance: [{}] cm. Dead end!".format(str(recovered_distance)))
        say_no()
        backward(0.5)
        rand = random.randint(0,100)
        print("rand: [{}]".format(str(rand)))
        if rand >= 0 and rand < 40:
            turn_left()
        if rand >= 40 and rand < 80:
            turn_right()
        if rand >= 80:
            random_move(force=True)
        recovered_distance = distanceMeasurement(trigger, echo)

    shutdown()
    print("Done")


if __name__ == '__main__':
    main()
