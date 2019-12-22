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


global default_config
default_config = robots_common.default_config


class RaspberryPi(robots_common.RobotHollow):
    def __init__(self, config={}, config_file=""):
        super().__init__()
        self.running = False
        self.config = config
        self.config_file = config_file
        self.name = "RaspberryPi"
        self.duty = 0.5
        self.duty_ratio = [1.0, 1.0, 1.0, 1.0]
        self.turn_right_period = 0.005
        self.turn_left_period = 0.005
        self._load_config()
        period = 0.02
        if "period" in self.config:
            period = self.config["period"]

        self.grab = True
        self.servo_claw = 0
        self.servo_claw_angle_open = -60
        self.servo_claw_angle_close = 60

        self.IN1 = 7
        self.IN2 = 8
        self.IN3 = 9
        self.IN4 = 10

        GPIO_SERVOS = [17]

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

    def _load_config(self):
        if len(self.config_file) and os.path.isfile(self.config_file):
            with open(self.config_file, "r") as f:
                json.load(self.config, f)
        for key in default_config:
            if key not in self.config:
                self.config[key] = default_config[key]
        if "name" in self.config:
            self.name = self.config.get("name")

    def shutdown(self, quiet=False):
        self.print_stdout("shutdown(quiet={})".format(quiet), quiet)
        self.running = False

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

    def move_forward(self, blocks=1, speed=0.5, quiet=False):
        self.print_stdout("move_forward(blocks={}, speed={})".format(blocks, speed), quiet)
        period = blocks/speed
        for motor in self.motors:
            motor.forward(speed)
        self.sleep(period, quiet=True)
        for motor in self.motors:
            motor.stop()

    def move_backwards(self, blocks=1, speed=0.5, quiet=False):
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


def test():
    a = RaspberryPi()
    print("Test 005")
    a.claw_open()
    a.sleep(1)
    a.claw_close()
    d = a.read_distance()
    print(d)
    a.move_forward()
    time.sleep(1)
    a.turn_right()
    time.sleep(1)
    a.turn_left()
    time.sleep(1)
    a.move_backwards()
    time.sleep(1)
    a.set_motor(1, -1)
    time.sleep(1)
    a.set_motor(2, 0.6)
    time.sleep(4)
    a.set_motor(1, 0)
    a.set_motor(2, 0)
    time.sleep(1)
    a.move_forward()
    a.shutdown()


#test()

