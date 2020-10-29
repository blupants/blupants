import os
import time
import json
import ev3dev2.motor as motor
import ev3dev2.sound as sound
import ev3dev2.sensor as sensor
import ev3dev2.sensor.lego as lego

try:
    import robots_common
except:
    import blupants.robots_common as robots_common


class EV3(robots_common.RobotHollow):
    def __init__(self):
        super().__init__()
        self.running = False

        self.reload()

        self.motors = []
        try:
            self.motors.append(motor.LargeMotor(motor.OUTPUT_A))
        except:
            pass
        try:
            self.motors.append(motor.LargeMotor(motor.OUTPUT_B))
        except:
            pass
        try:
            self.motors.append(motor.LargeMotor(motor.OUTPUT_C))
        except:
            pass
        try:
            self.motors.append(motor.LargeMotor(motor.OUTPUT_D))
        except:
            pass

        self.servos = []
        try:
            self.servos.append(motor.MediumMotor(motor.OUTPUT_A))
            self._servo_counter += 1
        except:
            pass
        try:
            self.servos.append(motor.MediumMotor(motor.OUTPUT_B))
            self._servo_counter += 1
        except:
            pass
        try:
            self.servos.append(motor.MediumMotor(motor.OUTPUT_C))
            self._servo_counter += 1
        except:
            pass
        try:
            self.servos.append(motor.MediumMotor(motor.OUTPUT_D))
            self._servo_counter += 1
        except:
            pass

        self.sound = None
        try:
            self.sound = sound.Sound()
        except:
            pass

        self.infrared_sensor = None
        try:
            self.infrared_sensor = lego.InfraredSensor(sensor.INPUT_4)
        except:
            pass

        self.ultrasonic_sensor = None
        if self.infrared_sensor == None:
            try:
                self.ultrasonic_sensor = lego.UltrasonicSensor(sensor.INPUT_4)
            except:
                pass

        self.running = True

    def reload(self):
        super().reload()
        self.name = self.config["name"]
        self.enable_tts = self.config["enable_tts"]
        self.period = self.config["period"]
        self.duty = self.config["duty"]
        self.block_length = self.config["block_length"]

    def shutdown(self, quiet=False):
        self.print_stdout("shutdown(quiet={})".format(quiet), quiet)
        self.say("Goodbye!", quiet)
        self.running = False

    def sleep(self, seconds=1.0, quiet=False):
        self.print_stdout("sleep(seconds={})".format(seconds), quiet)
        seconds_message = "seconds"
        if -2 < seconds < 2:
            seconds_message = "second"
        time.sleep(seconds)

    def set_servo(self, i=1, angle=0.0, quiet=False):
        self.print_stdout("set_servo(i={}, angle={})".format(i, angle), quiet)
        if str(i).lower() == "a":
            i = 1
        if str(i).lower() == "b":
            i = len(self.servos) - 2
        if str(i).lower() == "c":
            i = len(self.servos) - 1
        if str(i).lower() == "d":
            i = len(self.servos)
        try:
            self.servos[i - 1].on_for_degrees(30, angle)
        except:
            pass
        try:
            self.servos[i - 1].wait_until_not_moving()
        except:
            pass

    def set_motor(self, i=1, duty=0.5, quiet=False):
        self.print_stdout("set_motor(i={}, duty={})".format(i, duty), quiet)
        if str(i).lower() == "a":
            i = 1
        if str(i).lower() == "b":
            i = len(self.motors) - 2
        if str(i).lower() == "c":
            i = len(self.motors) - 1
        if str(i).lower() == "d":
            i = len(self.motors)
        speed_sp = duty * 1000
        time_sp = self.period * 1000
        try:
            self.motors[i - 1].run_timed(time_sp=time_sp, speed_sp=speed_sp)
        except:
            pass
        try:
            self.motors[i - 1].wait_until_not_moving()
        except:
            pass

    def read_distance(self, quiet=False):
        self.print_stdout("read_distance()", quiet)
        distance = -1
        try:
            system = self.config.get("measurement_system").lower()
        except:
            system = "m"

        if self.infrared_sensor:
            distance = self.infrared_sensor.proximity
        if self.ultrasonic_sensor:
            if system == "r" or system == "i" or system == "b":
                distance = self.ultrasonic_sensor.distance_centimeters
            else:
                distance = self.ultrasonic_sensor.distance_inches
        if system == "r" or system == "i" or system == "b":
            self.print_stdout("Distance: [{}] inches.".format(str(distance)), quiet)
        else:
            self.print_stdout("Distance: [{}] cm.".format(str(distance)), quiet)
        return distance

    def say(self, message, quiet=False):
        self.print_stdout(message, quiet)
        if not quiet and self.enable_tts:
            self.sound.speak(message)


class Gripp3r(EV3):
    def __init__(self):
        super().__init__()
        self.reload()

    def reload(self):
        super().reload()

        self.duty_ratio = self.config["ev3"]["motor"]["duty_ratio"]
        self.turn_right_period = 0.015
        self.turn_left_period = 0.015
        self.motor_front_left = 0
        self.motor_front_right = 1
        self.motor_back_left = 2
        self.motor_back_right = 3

        self.turn_right_period = self.config["ev3"]["motor"]["turn_right_period"]
        self.turn_left_period = self.config["ev3"]["motor"]["turn_left_period"]
        self.motor_front_left = self.config["ev3"]["motor"]["position"]["front_left"]
        self.motor_front_right = self.config["ev3"]["motor"]["position"]["front_right"]
        self.motor_back_left = self.config["ev3"]["motor"]["position"]["back_left"]
        self.motor_back_right = self.config["ev3"]["motor"]["position"]["back_right"]

        self.grab = True
        self._read_grab()

        self.servo_claw = "a"
        self.servo_claw_angle_open = -560
        self.servo_claw_angle_close = 560

        self.servo_claw = self.config["ev3"]["claw"]["servo"]
        self.servo_claw_angle_open = self.config["ev3"]["claw"]["angle_open"]
        self.servo_claw_angle_close = self.config["ev3"]["claw"]["angle_close"]

    def _read_grab(self):
        try:
            with open("/tmp/blupants/state", "r") as f:
                dict_state = json.load(f)
                self.grab = dict_state["claw_is_open"]
        except:
            pass

    def _set_grab(self, val):
        try:
            self.grab = val
            dict_state = {"claw_is_open": self.grab}
            with open("/tmp/blupants/state", "w") as f:
                json.dump(dict_state, f)
        except:
            pass

    def claw_toggle(self, quiet=False):
        if self.grab:
            self.claw_close(quiet)
        else:
            self.claw_open(quiet)

    def claw(self, quiet=False):
        return self.claw_toggle(quiet)

    def claw_open(self, quiet=False):
        self.print_stdout("claw_open()", quiet)
        if self.grab == False:
            self.set_servo(self.servo_claw, self.servo_claw_angle_open, quiet=True)
        self._set_grab(True)

    def claw_close(self, quiet=False):
        self.print_stdout("claw_close()", quiet)
        if self.grab == True:
            self.set_servo(self.servo_claw, self.servo_claw_angle_close, quiet=True)
        self._set_grab(False)

    def move(self, period=1, duty=1, quiet=False):
        self.print_stdout("move(period={}, duty={})".format(period, duty), quiet)
        speed_sp = duty * 1000
        time_sp = period * 1000
        for i in range(0, 4):
            try:
                motor_speed_sp = speed_sp * self.duty_ratio[i]
                self.motors[i].run_timed(time_sp=time_sp, speed_sp=motor_speed_sp)
            except:
                pass

        for i in range(0, 4):
            try:
                self.motors[i].wait_until_not_moving()
            except:
                pass

    def move_forward(self, blocks=1, speed=-1, quiet=False):
        if speed < 0:
            speed = self.duty
        self.print_stdout("move_forward(blocks={}, speed={})".format(blocks, speed), quiet)
        block_message = "blocks"
        if -2 < blocks < 2:
            block_message = "block"
        period = blocks * self.block_length / speed
        self.move(period, speed, quiet=True)

    def move_backwards(self, blocks=1, speed=-1, quiet=False):
        if speed < 0:
            speed = self.duty
        self.print_stdout("move_backwards(blocks={}, speed={})".format(blocks, speed), quiet)
        block_message = "blocks"
        if blocks > -2 and blocks < 2:
            block_message = "block"
        period = blocks * self.block_length / speed
        self.move(period, speed*-1, quiet=True)

    def turn_right(self, angle=90, quiet=False):
        self.print_stdout("turn_right(angle={})".format(angle), quiet)

        duty = 0.3  # Use fixed duty cycle for turning
        speed_sp = duty * 1000
        time_sp = angle * self.turn_right_period * 1000

        motor_front_left_running = False
        motor_back_left_running = False
        motor_front_right_running = False
        motor_back_right_running = False

        # Left
        try:
            self.motors[self.motor_front_left].run_timed(time_sp=time_sp, speed_sp=speed_sp)
            motor_front_left_running = True
        except:
            pass
        try:
            self.motors[self.motor_back_left].run_timed(time_sp=time_sp, speed_sp=speed_sp)
            motor_back_left_running = True
        except:
            pass

        # Right
        try:
            self.motors[self.motor_front_right].run_timed(time_sp=time_sp, speed_sp=speed_sp * -1)
            motor_front_right_running = True
        except:
            pass
        try:
            self.motors[self.motor_back_right].run_timed(time_sp=time_sp, speed_sp=speed_sp * -1)
            motor_back_right_running = True
        except:
            pass


        # Left
        try:
            if motor_front_left_running:
                self.motors[self.motor_front_left].wait_until_not_moving()
        except:
            pass
        try:
            if motor_back_left_running:
                self.motors[self.motor_back_left].wait_until_not_moving()
        except:
            pass

        # Right
        try:
            if motor_front_right_running:
                self.motors[self.motor_front_right].wait_until_not_moving()
        except:
            pass
        try:
            if motor_back_right_running:
                self.motors[self.motor_back_right].wait_until_not_moving()
        except:
            pass

    def turn_left(self, angle=90, quiet=False):
        self.print_stdout("turn_left(angle={})".format(angle), quiet)

        duty = 0.3  # Use fixed duty cycle for turning
        speed_sp = duty * 1000
        time_sp = angle * self.turn_left_period * 1000

        motor_front_left_running = False
        motor_back_left_running = False
        motor_front_right_running = False
        motor_back_right_running = False

        # Left
        try:
            self.motors[self.motor_front_left].run_timed(time_sp=time_sp, speed_sp=speed_sp * -1)
            motor_front_left_running = True
        except:
            pass
        try:
            self.motors[self.motor_back_left].run_timed(time_sp=time_sp, speed_sp=speed_sp * -1)
            motor_back_left_running = True
        except:
            pass

        # Right
        try:
            self.motors[self.motor_front_right].run_timed(time_sp=time_sp, speed_sp=speed_sp)
            motor_front_right_running = True
        except:
            pass
        try:
            self.motors[self.motor_back_right].run_timed(time_sp=time_sp, speed_sp=speed_sp)
            motor_back_right_running = True
        except:
            pass

        # Left
        try:
            if motor_front_left_running:
                self.motors[self.motor_front_left].wait_until_not_moving()
        except:
            pass
        try:
            if motor_back_left_running:
                self.motors[self.motor_back_left].wait_until_not_moving()
        except:
            pass

        # Right
        try:
            if motor_front_right_running:
                self.motors[self.motor_front_right].wait_until_not_moving()
        except:
            pass
        try:
            if motor_back_right_running:
                self.motors[self.motor_back_right].wait_until_not_moving()
        except:
            pass

    def say_yes(self, quiet=False):
        self.print_stdout("say_yes()", quiet)
        self.say("Yes!", quiet)

    def say_no(self, quiet=False):
        self.print_stdout("say_no()", quiet)
        self.say("No!", quiet)

    def say_welcome(self, quiet=False):
        self.print_stdout("say_welcome()", quiet)
        message = "Welcome to BluPants! My name is {} robot. Are you ready for learning Computer Science with me? " \
                  "Visit blupants.org to get started.".format(self.name)
        self.say(message, quiet)

