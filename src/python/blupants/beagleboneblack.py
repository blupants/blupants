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
    def __init__(self):
        super().__init__()
        self.running = False
        self.reload()
        self.look_angle(90)
        self.claw_open()
        self.running = True

    def reload(self):
        super().reload()
        if self.running:
            self.shutdown(quiet=False)
        self.name = self.config["name"]
        self.duty = self.config["duty"]
        self.duty_ratio = self.config["beagleboneblack"]["motor"]["duty_ratio"]
        self.turn_right_period = 0.03
        self.turn_right_period = self.config["beagleboneblack"]["motor"]["turn_right_period"]
        self.turn_left_period = 0.03
        self.turn_left_period = self.config["beagleboneblack"]["motor"]["turn_left_period"]

        self.grab = True
        self.servo_claw = 1
        self.servo_claw = self.config["beagleboneblack"]["claw"]["servo"]
        self.servo_claw_angle_open = -90
        self.servo_claw_angle_open = self.config["beagleboneblack"]["claw"]["angle_open"]
        self.servo_claw_angle_close = -30
        self.servo_claw_angle_close = self.config["beagleboneblack"]["claw"]["angle_close"]

        self.servo_horizontal = 2
        self.servo_horizontal = self.config["beagleboneblack"]["camera"]["servo_horizontal"]
        self.servo_vertical = 3
        self.servo_vertical = self.config["beagleboneblack"]["camera"]["servo_vertical"]

        self.ENA = "P9_21"
        self.IN1 = "P9_23"
        self.IN2 = "P9_27"
        self.IN3 = "P9_26"
        self.IN4 = "P9_24"
        self.ENB = "P9_22"

        self.ENA = self.config["beagleboneblack"]["motor"]["pinout"]["ENA"]
        self.IN1 = self.config["beagleboneblack"]["motor"]["pinout"]["IN1"]
        self.IN2 = self.config["beagleboneblack"]["motor"]["pinout"]["IN2"]
        self.IN3 = self.config["beagleboneblack"]["motor"]["pinout"]["IN3"]
        self.IN4 = self.config["beagleboneblack"]["motor"]["pinout"]["IN4"]
        self.ENB = self.config["beagleboneblack"]["motor"]["pinout"]["ENB"]

        PWM.start(self.ENA, 0, 1000)
        PWM.start(self.ENB, 0, 1000)
        GPIO.setup(self.IN1, GPIO.OUT)
        GPIO.setup(self.IN2, GPIO.OUT)
        GPIO.setup(self.IN3, GPIO.OUT)
        GPIO.setup(self.IN4, GPIO.OUT)

        self.GPIO_SERVOS = ["P8_13", "P9_42", "P8_19"]
        self.GPIO_SERVOS = self.config["beagleboneblack"]["servos"]

        for pin in self.GPIO_SERVOS:
            PWM.start(pin, 2, 50)

        self.trigger = "P8_12"
        self.echo = "P8_11"

        self.trigger = self.config["beagleboneblack"]["hcsr04"]["trigger"]
        self.echo = self.config["beagleboneblack"]["hcsr04"]["echo"]

        # Configuration
        GPIO.setup(self.trigger, GPIO.OUT)
        GPIO.setup(self.echo, GPIO.IN)

        # Security
        GPIO.output(self.trigger, False)
        time.sleep(0.5)

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
        duty = duty * self.duty_ratio[motor_index]
        enable = None
        if motor_index > 0:
            enable = self.ENB
            if duty < 0:
                GPIO.output(self.IN3, GPIO.HIGH)
                GPIO.output(self.IN4, GPIO.LOW)
            else:
                GPIO.output(self.IN3, GPIO.LOW)
                GPIO.output(self.IN4, GPIO.HIGH)
        else:
            enable = self.ENA
            if duty < 0:
                GPIO.output(self.IN1, GPIO.LOW)
                GPIO.output(self.IN2, GPIO.HIGH)
            else:
                GPIO.output(self.IN1, GPIO.HIGH)
                GPIO.output(self.IN2, GPIO.LOW)

        if duty < 0:
            duty *= -1
        if enable:
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
        self.set_motor(1, 0, quiet=True)
        self.set_motor(2, 0, quiet=True)

    def move_forward(self, blocks=1, speed=-1, quiet=False):
        if speed < 0:
            speed = self.duty
        self.print_stdout("move_forward(blocks={}, speed={})".format(blocks, speed), quiet)
        period = blocks/speed
        speed *= 100
        self.set_motor(1, speed, quiet=True)
        self.set_motor(2, speed, quiet=True)
        self.sleep(period, quiet=True)
        self._stop()

    def move_backwards(self, blocks=1, speed=-1, quiet=False):
        if speed < 0:
            speed = self.duty
        self.print_stdout("move_backwards(blocks={}, speed={})".format(blocks, speed), quiet)
        period = blocks/speed
        speed *= 100
        self.set_motor(1, speed * -1, quiet=True)
        self.set_motor(2, speed * -1, quiet=True)
        self.sleep(period, quiet=True)
        self._stop()

    def turn_right(self, angle=90, quiet=False):
        self.print_stdout("turn_right(angle={})".format(angle), quiet)
        duty = 30  # Use fixed duty cycle for turning

        # Left motor
        self.set_motor(1, duty, quiet=True)
        # Right motor
        self.set_motor(2, duty * -1, quiet=True)

        self.sleep(angle * self.turn_right_period, quiet=True)

        self._stop()

    def turn_left(self, angle=90, quiet=False):
        self.print_stdout("turn_left(angle={})".format(angle), quiet)
        duty = 30  # Use fixed duty cycle for turning

        # Left motor
        self.set_motor(1, duty * -1)
        # Right motor
        self.set_motor(2, duty)

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
    print("Test 005")

    # a.turn_left()
    # a.turn_right()

    # a.say_yes()

    # for i in range(0, 2):
    #     print(i)
    #     a.camera_toggle()
    #
    a.move_forward()
    a.sleep(5)
    a.move_backwards()
    #
    #a.look_angle(90)

    # a.test1ff()
    # a.test1back()
    # a.test1ff()

    # for i in range(0, 2):
    #     a.claw_toggle()
    #     d = a.read_distance()
    #     print("distance is: {}".format(d))
    #     time.sleep(2)
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
    # a.say_yes()
    # a.say_no()
    # for i in range(0, 11):
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
    # a.look_angle(90)
    a.shutdown()


#test()

