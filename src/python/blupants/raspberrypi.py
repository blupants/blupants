import sys
import os
import time
import random
import json
import time
from gpiozero import AngularServo
from gpiozero import Motor
from gpiozero import DistanceSensor

try:
    import robots_common
except:
    import blupants.robots_common as robots_common


class RaspberryPi(robots_common.RobotHollow):
    def __init__(self, config={}, config_file=""):
        super().__init__()
        self.running = False
        self.config = config
        self.config_file = config_file
        self.name = "RaspberryPi"
        self.duty = self.config["duty"]
        self.duty_ratio = [1.0, 1.0, 1.0, 1.0]
        self.turn_right_period = 0.005
        self.turn_left_period = 0.005
        period = 0.02
        if "period" in self.config:
            period = self.config["period"]

        self.camera_pos = 0
        self.camera_toggle_positions = [
            [-89.0, 0], [89.0, 0], [89.0, 30.0], [0, 30.0], [-89.0, 30.0], [-89.0, 0], [-89.0, -30.0], [0, -30.0],
            [89.0, -30.0], [89.0, 0], [0, 0]
        ]

        self.servo_horizontal = self.config["blupants"]["camera"]["servo_horizontal"]
        self.servo_vertical = self.config["blupants"]["camera"]["servo_vertical"]

        self.grab = True
        self.servo_claw = 1
        self.servo_claw_angle_open = -60
        self.servo_claw_angle_close = 60

        self.servo_horizontal = 2
        self.servo_vertical = 3

        self.IN1 = 7
        self.IN2 = 8
        self.IN3 = 9
        self.IN4 = 10

        GPIO_SERVOS = [17, 27, 22]

        GPIO_TRIGGER = 18
        GPIO_ECHO = 24

        motor_left = (self.IN1, self.IN2)
        motor_right = (self.IN3, self.IN4)

        self.motors = [Motor(forward=motor_left[0], backward=motor_left[1]),
                       Motor(forward=motor_right[0], backward=motor_right[1])]

        self.pi_servos = []
        for gpio_servo in GPIO_SERVOS:
            self.pi_servos.append(AngularServo(gpio_servo, min_angle=-90, max_angle=90))

        self.hcsr04 = DistanceSensor(echo=GPIO_ECHO, trigger=GPIO_TRIGGER)

        self.running = True

    def shutdown(self, quiet=False):
        self.print_stdout("shutdown(quiet={})".format(quiet), quiet)
        self.running = False
        self.hcsr04.close()
        for servo in self.pi_servos:
            servo.close()
        for motor in self.motors:
            motor.close()

    def sleep(self, seconds=1.0, quiet=False):
        self.print_stdout("sleep(seconds={})".format(seconds), quiet)
        time.sleep(seconds)

    def set_servo(self, i=1, angle=0.0, quiet=False):
        self.print_stdout("set_servo(i={}, angle={})".format(i, angle), quiet)
        time.sleep(0.2)
        if angle > 0 and angle > 90:
            angle = 90
        if angle < 0 and angle < -90:
            angle = -90
        self.pi_servos[i - 1].angle = angle
        time.sleep(0.2)

    def set_motor(self, i=1, duty=0.5, quiet=False):
        self.print_stdout("set_motor(i={}, duty={})".format(i, duty), quiet)
        motor_index = i-1
        if duty < 0:
            duty *= -1
            self.motors[motor_index].backward(duty)
        else:
            self.motors[motor_index].forward(duty)
        if -0.01 <= duty <= 0.01:
            self.motors[motor_index].stop()

    def claw_toggle(self, quiet=False):
        if self.grab:
            self.claw_close(quiet)
        else:
            self.claw_open(quiet)

    def claw_open(self, quiet=False):
        self.print_stdout("claw_open()", quiet)
        self.grab = True
        self.set_servo(self.servo_claw, self.servo_claw_angle_open, quiet=True)

    def claw_close(self, quiet=False):
        self.print_stdout("claw_close()", quiet)
        self.grab = False
        self.set_servo(self.servo_claw, self.servo_claw_angle_close, quiet=True)

    def read_distance(self, quiet=False):
        # Read sonar
        distance = self.hcsr04.distance * 100
        try:
            system = self.config.get("measurement_system").lower()
        except:
            system = "m"
        if system == "r" or system == "i" or system == "b":
            distance = distance * 0.393701
            self.print_stdout("Distance: [{}] inches.".format(str(distance)), quiet)
        else:
            self.print_stdout("Distance: [{}] cm.".format(str(distance)), quiet)
        return distance

    def move_forward(self, blocks=1, speed=-1, quiet=False):
        if speed < 0:
            speed = self.duty
        self.print_stdout("move_forward(blocks={}, speed={})".format(blocks, speed), quiet)
        period = blocks/speed
        for motor in self.motors:
            motor.forward(speed)
        self.sleep(period, quiet=True)
        for motor in self.motors:
            motor.stop()

    def move_backwards(self, blocks=1, speed=-1, quiet=False):
        if speed < 0:
            speed = self.duty
        self.print_stdout("move_backwards(blocks={}, speed={})".format(blocks, speed), quiet)
        period = blocks/speed
        for motor in self.motors:
            motor.backward(speed)
        self.sleep(period, quiet=True)
        for motor in self.motors:
            motor.stop()

    def turn_right(self, angle=90, quiet=False):
        self.print_stdout("turn_right(angle={})".format(angle), quiet)
        duty = 0.5  # Use fixed duty cycle for turning
        index=0
        for motor in self.motors:
            if index % 2 == 0:
                # Left motor
                motor.forward(duty)
            else:
                # Right motor
                motor.backward(duty)
            index+=1
        self.sleep(angle * self.turn_right_period, quiet=True)
        for motor in self.motors:
            motor.stop()

    def turn_left(self, angle=90, quiet=False):
        self.print_stdout("turn_left(angle={})".format(angle), quiet)
        duty = 0.5  # Use fixed duty cycle for turning
        index=0
        for motor in self.motors:
            if index % 2 == 0:
                # Left motor
                motor.backward(duty)
            else:
                # Right motor
                motor.forward(duty)
            index+=1
        self.sleep(angle * self.turn_left_period, quiet=True)
        for motor in self.motors:
            motor.stop()

    def camera_toggle(self, quiet=False):
        self.print_stdout("camera_toggle()", quiet)
        max = len(self.camera_toggle_positions)
        if self.camera_pos >= max:
            self.camera_pos = 0
        pos = self.camera_toggle_positions[self.camera_pos]
        self.sleep(0.2, quiet=True)
        self.set_servo(self.servo_horizontal, pos[0], quiet=True)
        self.sleep(0.2, quiet=True)
        self.set_servo(self.servo_vertical, pos[1], quiet=True)
        self.sleep(0.2, quiet=True)
        self.camera_pos += 1

    def look_angle(self, angle=90, quiet=False):
        self.print_stdout("look_angle(angle={})".format(angle), quiet)
        self.sleep(0.2, quiet=True)
        if angle > 0 and angle > 90:
            angle = 90
        if angle < 0 and angle < -90:
            angle = -90
        position = angle * 0.015
        self.set_servo(self.servo_horizontal, position, quiet=True)
        self.set_servo(self.servo_vertical, 0, quiet=True)
        self.sleep(0.2, quiet=True)

    def say_yes(self, quiet=False):
        self.print_stdout("say_yes()", quiet)
        self.look_angle(0, quiet=True)
        self.set_servo(self.servo_vertical, 60.0, quiet=True)
        self.set_servo(self.servo_vertical, -60.0, quiet=True)
        self.set_servo(self.servo_vertical, 60.0, quiet=True)
        self.look_angle(0, quiet=True)

    def say_no(self, quiet=False):
        self.print_stdout("say_no()", quiet)
        self.look_angle(0, quiet=True)
        self.set_servo(self.servo_horizontal, 60.0, quiet=True)
        self.set_servo(self.servo_horizontal, -60.0, quiet=True)
        self.set_servo(self.servo_horizontal, 60.0, quiet=True)
        self.look_angle(0, quiet=True)


def test():
    a = RaspberryPi()
    print("Test 005")
    a.say_yes()
    #a.claw_open()
    a.sleep(1)
    #a.claw_close()
    a.say_no()
    for i in range(0, 20):
        a.camera_toggle()
        print(i)
        time.sleep(0.3)
    a.say_no()
    a.look_angle(0)
    a.sleep(1)
    # d = a.read_distance()
    # print(d)
    # a.move_forward()
    # time.sleep(1)
    # a.turn_right()
    # time.sleep(1)
    # a.turn_left()
    # time.sleep(1)
    # a.move_backwards()
    # time.sleep(1)
    # a.set_motor(1, -1)
    # time.sleep(1)
    # a.set_motor(2, 0.6)
    # time.sleep(4)
    # a.set_motor(1, 0)
    # a.set_motor(2, 0)
    # time.sleep(1)
    # a.move_forward()
    a.shutdown()


#test()

