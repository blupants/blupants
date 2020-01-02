import sys
import os
import time
import random
import json
import time
import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM

try:
    import robots_common
except:
    import blupants.robots_common as robots_common


global default_config
default_config = robots_common.default_config


class BeagleBoneBlack(robots_common.RobotHollow):
    def __init__(self, config={}, config_file=""):
        super().__init__()
        self.running = False
        self.config = config
        self.config_file = config_file
        self.name = "BeagleBoneBlack"
        self.duty = 0.5
        self.duty_ratio = [1.0, 1.0, 1.0, 1.0]
        self.turn_right_period = 0.005
        self.turn_left_period = 0.005
        self._load_config()
        period = 0.02
        if "period" in self.config:
            period = self.config["period"]

        self.camera_pos = 0
        self.camera_toggle_positions = [
            [-89.0, 0], [89.0, 0], [89.0, 30.0], [0, 30.0], [-89.0, 30.0], [-89.0, 0], [-89.0, -30.0], [0, -30.0],
            [89.0, -30.0], [89.0, 0], [0, 0]
        ]

        if "blupants" in self.config:
            if "camera" in self.config["blupants"]:
                if "servo_horizontal" in self.config["blupants"]["camera"]:
                    self.servo_horizontal = self.config["blupants"]["camera"]["servo_horizontal"]
                if "servo_vertical" in self.config["blupants"]["camera"]:
                    self.servo_vertical = self.config["blupants"]["camera"]["servo_vertical"]

        self.grab = True
        self.servo_claw = 1
        self.servo_claw_angle_open = -90
        self.servo_claw_angle_close = -30

        self.servo_horizontal = 2
        self.servo_vertical = 3

        self.ENA = "P9_22"
        self.IN1 = "P9_23"
        self.IN2 = "P9_14"
        self.IN3 = "P9_15"
        self.IN4 = "P9_16"
        self.ENB = "P9_21"

        PWM.start(self.ENA, 0, 1000)
        PWM.start(self.ENB, 0, 1000)
        GPIO.setup(self.IN1, GPIO.OUT)
        GPIO.setup(self.IN2, GPIO.OUT)
        GPIO.setup(self.IN3, GPIO.OUT)
        GPIO.setup(self.IN4, GPIO.OUT)

        self.GPIO_SERVOS = ["P8_13", "P9_42", "P8_19"]

        for pin in self.GPIO_SERVOS:
            PWM.start(pin, 2, 50)

        self.trigger = "P8_12"
        self.echo = "P8_11"

        # Configuration
        GPIO.setup(self.trigger, GPIO.OUT)
        GPIO.setup(self.echo, GPIO.IN)

        # Security
        GPIO.output(self.trigger, False)
        time.sleep(0.5)

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
        PWM.cleanup()
        GPIO.cleanup()

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

        angle += 90

        servo_pin = self.GPIO_SERVOS[i - 1]
        dc = (11.0/180.0 * angle) + 2
        PWM.set_duty_cycle(servo_pin, dc)
        time.sleep(0.2)

    def set_motor(self, i=1, duty=0.5, quiet=False):
        self.print_stdout("set_motor(i={}, duty={})".format(i, duty), quiet)
        motor_index = i-1
        if duty < 0:
            duty *= -1

        if duty < 0:
            GPIO.output(self.IN1, GPIO.HIGH)
            GPIO.output(self.IN2, GPIO.LOW)
            GPIO.output(self.IN3, GPIO.HIGH)
            GPIO.output(self.IN4, GPIO.LOW)
        else:
            GPIO.output(self.IN1, GPIO.LOW)
            GPIO.output(self.IN2, GPIO.HIGH)
            GPIO.output(self.IN3, GPIO.LOW)
            GPIO.output(self.IN4, GPIO.HIGH)
        enable = self.ENA
        if motor_index > 0:
            enable = self.ENB
        PWM.set_duty_cycle(enable, duty)

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

    def _distance_measurement(self):
        max = 10000
        GPIO.output(self.trigger, True)
        time.sleep(0.00001)
        GPIO.output(self.trigger, False)
        pulse_start = time.time()
        pulse_end = time.time()
        counter = 0
        while GPIO.input(self.echo) == 0:
            pulse_start = time.time()
            counter += 1
            if counter > max:
                return -1
        counter = 0
        while GPIO.input(self.echo) == 1:
            pulse_end = time.time()
            counter += 1
            if counter > max:
                return -1

        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150
        distance = round(distance, 2)
        return distance

    def read_distance(self, quiet=False):
        # Read sonar
        distance = self._distance_measurement()
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

    def _stop(self):
        self.set_motor(0, 0, quiet=True)
        self.set_motor(1, 0, quiet=True)

    def move_forward(self, blocks=1, speed=0.5, quiet=False):
        self.print_stdout("move_forward(blocks={}, speed={})".format(blocks, speed), quiet)
        period = blocks/speed
        self.set_motor(0, speed, quiet=True)
        self.set_motor(1, speed, quiet=True)
        self.sleep(period, quiet=True)
        self._stop()

    def move_backwards(self, blocks=1, speed=0.5, quiet=False):
        self.print_stdout("move_backwards(blocks={}, speed={})".format(blocks, speed), quiet)
        period = blocks/speed
        self.set_motor(0, speed * -1, quiet=True)
        self.set_motor(1, speed * -1, quiet=True)
        self.sleep(period, quiet=True)
        self._stop()

    def turn_right(self, angle=90, quiet=False):
        self.print_stdout("turn_right(angle={})".format(angle), quiet)
        duty = 0.5  # Use fixed duty cycle for turning

        # Left motor
        self.set_motor(0, duty, quiet=True)
        # Right motor
        self.set_motor(1, duty * -1, quiet=True)

        self.sleep(angle * self.turn_right_period, quiet=True)

        self._stop()

    def turn_left(self, angle=90, quiet=False):
        self.print_stdout("turn_left(angle={})".format(angle), quiet)
        duty = 0.5  # Use fixed duty cycle for turning

        # Left motor
        self.set_motor(0, duty * -1)
        # Right motor
        self.set_motor(1, duty)

        self.sleep(angle * self.turn_right_period, quiet=True)

        self._stop()

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
    a = BeagleBoneBlack()
    print("Test 001")
    # a.say_yes()

    for i in range(0, 10):
        a.claw_toggle()
        d = a.read_distance()
        print("distance is: {}".format(d))
        time.sleep(2)
    # a.set_servo(1, -30)
    # a.sleep(3)
    # a.set_servo(1, -40)
    # a.sleep(3)
    # a.set_servo(1, -50)
    # a.sleep(3)
    # a.set_servo(1, -60)
    # a.sleep(3)
    # a.set_servo(1, -70)
    # a.sleep(3)
    # a.set_servo(1, -80)
    # a.sleep(3)
    # a.set_servo(1, -90)
    # a.sleep(3)
    # a.set_servo(1, -30)
    # a.sleep(3)
    # a.set_servo(1, 45)
    # a.sleep(5)
    # a.set_servo(1, 90)
    # a.sleep(5)
    # a.set_servo(1, 45)
    # a.sleep(5)
    # a.set_servo(1, 0)
    # a.sleep(5)
    # a.set_servo(1, -45)
    # a.sleep(5)
    # a.set_servo(1, -90)
    # a.sleep(5)

    # dc = 1.0 / 18.0 * 90
    # PWM.set_duty_cycle("P8_13", dc)
    # a.sleep(3)

    # for i in range(0, 12):
    #     print(i)
    #     PWM.set_duty_cycle("P8_13", i)
    #     time.sleep(3)

    # begin = 2
    # end = 13
    #
    # PWM.set_duty_cycle("P8_13", begin)
    # time.sleep(3)
    #
    # PWM.set_duty_cycle("P8_13", end)
    # time.sleep(3)
    #
    # PWM.set_duty_cycle("P8_13", begin)
    # time.sleep(3)
    #
    # PWM.set_duty_cycle("P8_13", end)
    # time.sleep(3)
    #
    # PWM.set_duty_cycle("P8_13", begin)
    # time.sleep(3)



    # a.claw_open()
    # a.sleep(5)
    # a.claw_close()
    # a.sleep(2)
    # a.say_no()
    # for i in range(0, 20):
    #     a.camera_toggle()
    #     print(i)
    #     time.sleep(0.3)
    # a.say_no()
    # a.look_angle(0)
    # a.sleep(1)
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


test()

