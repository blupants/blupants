import sys
import os
import time
import random
import json
import time
import pyttsx3
import RPi.GPIO as GPIO
from gpiozero import Motor
import time
import math
import smbus

try:
    import robots_common
except:
    import blupants.robots_common as robots_common


class AlphaBot2(robots_common.RobotHollow):
    def __init__(self):
        super().__init__()
        self.running = False
        self.reload()
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)
        self.running = True

    def reload(self):
        super().reload()

        self.name = "AlphaBot2"
        self.duty = self.config["duty"]
        self.block_length = self.config["block_length"]
        self.duty_ratio = self.duty_ratio = self.config["alphabot"]["motor"]["duty_ratio"]
        self.turn_right_period = 0.005
        self.turn_left_period = 0.005
        self.turn_right_period = self.config["alphabot"]["motor"]["turn_right_period"]
        self.turn_left_period = self.config["alphabot"]["motor"]["turn_left_period"]

        self.servo_horizontal = self.config["alphabot"]["camera"]["servo_horizontal"]
        self.servo_vertical = self.config["alphabot"]["camera"]["servo_vertical"]

        self.grab = True
        self.servo_claw = 1
        self.servo_claw_angle_open = -60
        self.servo_claw_angle_close = 60

        self.servo_claw = self.config["alphabot"]["claw"]["servo"]
        self.servo_claw_angle_open = self.config["alphabot"]["claw"]["angle_open"]
        self.servo_claw_angle_close = self.config["alphabot"]["claw"]["angle_close"]

        self.servo_horizontal = 2
        self.servo_vertical = 3

        self.servo_horizontal = self.config["alphabot"]["camera"]["servo_horizontal"]
        self.servo_vertical = self.config["alphabot"]["camera"]["servo_vertical"]

        self.ENA = 6
        self.AIN1 = 12
        self.AIN2 = 13
        self.BIN1 = 20
        self.BIN2 = 21
        self.ENB = 26

        self.ENA = self.config["alphabot"]["motor"]["pinout"]["ENA"]
        self.AIN1 = self.config["alphabot"]["motor"]["pinout"]["AIN1"]
        self.AIN2 = self.config["alphabot"]["motor"]["pinout"]["AIN2"]
        self.BIN1 = self.config["alphabot"]["motor"]["pinout"]["BIN1"]
        self.BIN2 = self.config["alphabot"]["motor"]["pinout"]["BIN2"]
        self.ENB = self.config["alphabot"]["motor"]["pinout"]["ENB"]

        self.trigger = 22
        self.echo = 27

        self.trigger = self.config["alphabot"]["hcsr04"]["trigger"]
        self.echo = self.config["alphabot"]["hcsr04"]["echo"]

        motor_left = [self.AIN1, self.AIN2]
        motor_right = [self.BIN1, self.BIN2]

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(True)

        self.motors = [Motor(backward=motor_left[0], forward=motor_left[1], enable=self.ENA),
                       Motor(backward=motor_right[0], forward=motor_right[1], enable=self.ENB)]

        GPIO.setup(self.trigger, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.echo, GPIO.IN)

        self.pwm = PCA9685(0x40, debug=False)
        self.pwm.setPWMFreq(50)

    def shutdown(self, quiet=False):
        self.print_stdout("shutdown(quiet={})".format(quiet), quiet)
        self.running = False
        for motor in self.motors:
            motor.close()
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
        angle = (angle * 11.11) + 1500
        if angle < 100:
            angle = 100
        self.pwm.setServoPulse(i, angle)
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
        distance = -1
        GPIO.output(self.trigger, GPIO.HIGH)
        time.sleep(0.000015)
        GPIO.output(self.trigger, GPIO.LOW)
        while not GPIO.input(self.echo):
            pass
        t1 = time.time()
        while GPIO.input(self.echo):
            pass
        t2 = time.time()
        distance = (t2 - t1) * 34000 / 2
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
        period = blocks * self.block_length / speed
        motor_index = 0
        for motor in self.motors:
            motor_speed = speed * self.duty_ratio[motor_index]
            motor.forward(motor_speed)
            motor_index += 1
        self.sleep(period, quiet=True)
        for motor in self.motors:
            motor.stop()
        time.sleep(0.5)

    def move_backwards(self, blocks=1, speed=-1, quiet=False):
        if speed < 0:
            speed = self.duty
        self.print_stdout("move_backwards(blocks={}, speed={})".format(blocks, speed), quiet)
        period = blocks * self.block_length / speed
        motor_index = 0
        for motor in self.motors:
            motor_speed = speed * self.duty_ratio[motor_index]
            motor.backward(motor_speed)
            motor_index += 1
        self.sleep(period, quiet=True)
        for motor in self.motors:
            motor.stop()
        time.sleep(0.5)

    def turn_right(self, angle=90, quiet=False):
        self.print_stdout("turn_right(angle={})".format(angle), quiet)
        duty = 0.2  # Use fixed duty cycle for turning
        index = 0
        for motor in self.motors:
            if index % 2 == 0:
                # Left motor
                motor.forward(duty)
            else:
                # Right motor
                motor.backward(duty)
            index += 1
        self.sleep(angle * self.turn_right_period, quiet=True)
        for motor in self.motors:
            motor.stop()
        time.sleep(0.5)

    def turn_left(self, angle=90, quiet=False):
        self.print_stdout("turn_left(angle={})".format(angle), quiet)
        duty = 0.2  # Use fixed duty cycle for turning
        index = 0
        for motor in self.motors:
            if index % 2 == 0:
                # Left motor
                motor.backward(duty)
            else:
                # Right motor
                motor.forward(duty)
            index += 1
        self.sleep(angle * self.turn_left_period, quiet=True)
        for motor in self.motors:
            motor.stop()
        time.sleep(0.5)

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
        self.say("Yes!", quiet)
        self.set_servo(self.servo_vertical, 60.0, quiet=True)
        self.set_servo(self.servo_vertical, -60.0, quiet=True)
        self.set_servo(self.servo_vertical, 60.0, quiet=True)
        self.look_angle(0, quiet=True)

    def say_no(self, quiet=False):
        self.print_stdout("say_no()", quiet)
        self.look_angle(0, quiet=True)
        self.say("No!", quiet)
        self.set_servo(self.servo_horizontal, 60.0, quiet=True)
        self.set_servo(self.servo_horizontal, -60.0, quiet=True)
        self.set_servo(self.servo_horizontal, 60.0, quiet=True)
        self.look_angle(0, quiet=True)

    def say_welcome(self, quiet=False):
        self.print_stdout("say_welcome()", quiet)
        self.say_yes(True)
        message = "Welcome to BluPants! My name is {} robot. Are you ready for learning Computer Science with me? " \
                  "Visit blupants.org to get started.".format(self.name)
        self.say(message, quiet)

    def say(self, message, quiet=False):
        self.print_stdout(message, quiet)
        if not quiet:
            try:
                self.tts_engine.say(message)
                self.tts_engine.runAndWait()
            except:
                pass


# ============================================================================
# Raspi PCA9685 16-Channel PWM Servo Driver
# ============================================================================

class PCA9685:
    # Registers/etc.
    __SUBADR1 = 0x02
    __SUBADR2 = 0x03
    __SUBADR3 = 0x04
    __MODE1 = 0x00
    __PRESCALE = 0xFE
    __LED0_ON_L = 0x06
    __LED0_ON_H = 0x07
    __LED0_OFF_L = 0x08
    __LED0_OFF_H = 0x09
    __ALLLED_ON_L = 0xFA
    __ALLLED_ON_H = 0xFB
    __ALLLED_OFF_L = 0xFC
    __ALLLED_OFF_H = 0xFD

    def __init__(self, address=0x40, debug=False):
        self.bus = smbus.SMBus(1)
        self.address = address
        self.debug = debug
        if (self.debug):
            print("Reseting PCA9685")
        self.write(self.__MODE1, 0x00)

    def write(self, reg, value):
        "Writes an 8-bit value to the specified register/address"
        self.bus.write_byte_data(self.address, reg, value)
        if (self.debug):
            print("I2C: Write 0x%02X to register 0x%02X" % (value, reg))

    def read(self, reg):
        "Read an unsigned byte from the I2C device"
        result = self.bus.read_byte_data(self.address, reg)
        if (self.debug):
            print("I2C: Device 0x%02X returned 0x%02X from reg 0x%02X" % (self.address, result & 0xFF, reg))
        return result

    def setPWMFreq(self, freq):
        "Sets the PWM frequency"
        prescaleval = 25000000.0  # 25MHz
        prescaleval /= 4096.0  # 12-bit
        prescaleval /= float(freq)
        prescaleval -= 1.0
        if (self.debug):
            print("Setting PWM frequency to %d Hz" % freq)
            print("Estimated pre-scale: %d" % prescaleval)
        prescale = math.floor(prescaleval + 0.5)
        if (self.debug):
            print("Final pre-scale: %d" % prescale)

        oldmode = self.read(self.__MODE1);
        newmode = (oldmode & 0x7F) | 0x10  # sleep
        self.write(self.__MODE1, newmode)  # go to sleep
        self.write(self.__PRESCALE, int(math.floor(prescale)))
        self.write(self.__MODE1, oldmode)
        time.sleep(0.005)
        self.write(self.__MODE1, oldmode | 0x80)

    def setPWM(self, channel, on, off):
        "Sets a single PWM channel"
        on = int(on)
        off = int(off)
        self.write(self.__LED0_ON_L + 4 * channel, on & 0xFF)
        self.write(self.__LED0_ON_H + 4 * channel, on >> 8)
        self.write(self.__LED0_OFF_L + 4 * channel, off & 0xFF)
        self.write(self.__LED0_OFF_H + 4 * channel, off >> 8)
        if (self.debug):
            print("channel: %d  LED_ON: %d LED_OFF: %d" % (channel, on, off))

    def setServoPulse(self, channel, pulse):
        "Sets the Servo Pulse,The PWM frequency must be 50HZ"
        pulse = pulse * 4096 / 20000  # PWM frequency is 50HZ,the period is 20000us
        self.setPWM(channel, 0, pulse)


def test():
    a = AlphaBot2()
    print("Test 002")

    robot = a
    robot.move_forward(2)
    time.sleep(1)
    robot.move_backwards(2)
    time.sleep(1)
    # robot.set_servo(1, 45)
    # robot.move_forward(1)
    # robot.set_servo(1, 0)
    # robot.turn_right(90)
    # robot.move_forward(1)
    # robot.move_backwards(1)
    # robot.turn_left(90)

    # for i in range(0, 16):
    #     a.camera_toggle()
    #     a.sleep(0.5)
    #
    # a.set_servo(0, 0)
    # a.set_servo(1, 0)
    # a.sleep(1)

    d = a.read_distance()
    print(d)
    servo = 0
    # a.set_servo(servo, 90)
    # a.sleep(1)
    # a.set_servo(servo, -90)
    # a.sleep(1)
    # a.set_servo(servo, 45)
    # a.sleep(1)
    # a.set_servo(servo, -45)
    # a.sleep(1)
    # a.set_servo(servo, 90)
    # a.sleep(1)
    # a.set_servo(servo, 0)
    # a.sleep(1)

    #a.turn_left()

    # a.say_yes()

    a.shutdown()

#test()
