import sys
import os
import time
import random
import json
import pyttsx3
import rcpy
import rcpy.motor as motor
import rcpy.servo as servo
import rcpy.clock as clock
import rcpy.gpio as gpio
from rcpy.gpio import InputEvent
import Adafruit_BBIO.GPIO as GPIO

try:
    import robots_common
except:
    import blupants.robots_common as robots_common

class BeagleBoneBlue(robots_common.RobotHollow):
    def __init__(self):
        super().__init__()
        self.servo_angle_factor = 0.015
        self.running = False
        self.reload()
        period = self.period

        init_servo_duty = []
        self.cur_angles = self.config.get("beagleboneblue", {}).get("servo", {}).get("init_angle", [0, 0, 0, 0, 0, 0, 0, 0])
        for i in range(0, 8):
            ang = 0
            if len(self.cur_angles) > i:
                ang = self.cur_angles[i] * self.servo_angle_factor
            init_servo_duty.append(ang)

        self.bbb_servos = [servo.Servo(1, init_servo_duty[0]), servo.Servo(2, init_servo_duty[1]), servo.Servo(3, init_servo_duty[2]), servo.Servo(4, init_servo_duty[3]),
                           servo.Servo(5, init_servo_duty[4]), servo.Servo(6, init_servo_duty[5]), servo.Servo(7, init_servo_duty[6]), servo.Servo(8, init_servo_duty[7])]

        self.clcks = [clock.Clock(self.bbb_servos[0], period), clock.Clock(self.bbb_servos[1], period),
                      clock.Clock(self.bbb_servos[2], period), clock.Clock(self.bbb_servos[3], period),
                      clock.Clock(self.bbb_servos[4], period), clock.Clock(self.bbb_servos[5], period),
                      clock.Clock(self.bbb_servos[6], period), clock.Clock(self.bbb_servos[7], period)]

        self.motors = [motor.Motor(1), motor.Motor(2), motor.Motor(3), motor.Motor(4)]

        # Boot
        GPIO.cleanup()
        rcpy.set_state(rcpy.RUNNING)
        # disable servos
        servo.enable()
        # start clock
        for i in range(0, 8):
            self.clcks[i].start()

        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)
        self.running = True

    def reload(self):
        super().reload()
        self.name = self.config["name"]
        self.period = self.config["period"]

    def shutdown(self, quiet=False):
        self.print_stdout("shutdown(quiet={})".format(quiet), quiet)
        self.running = False
        # stop clock
        for i in range(0, 8):
            self.clcks[i].stop()
        # disable servos
        servo.disable()
        rcpy.set_state(rcpy.EXITING)
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
        position = angle * self.servo_angle_factor
        self.bbb_servos[i - 1].set(position)
        self.cur_angles[i -1] = angle
        time.sleep(0.2)

    def set_motor(self, i=1, duty=0.5, quiet=False):
        self.print_stdout("set_motor(i={}, duty={})".format(i, duty), quiet)
        motor_index = i-1
        self.motors[motor_index].set(duty)


class BluPants(BeagleBoneBlue):
    def __init__(self):
        super().__init__()
        self.reload()

    def reload(self):
        super().reload()
        self.duty = self.config["duty"]
        self.block_length = self.config["block_length"]
        self.enable_tts = self.config["enable_tts"]
        self.duty_ratio = self.config["beagleboneblue"]["motor"]["duty_ratio"]
        self.turn_right_period = self.config["beagleboneblue"]["motor"]["turn_right_period"]
        self.turn_left_period = self.config["beagleboneblue"]["motor"]["turn_left_period"]
        self.motor_front_left = self.config["beagleboneblue"]["motor"]["position"]["front_left"]
        self.motor_front_right = self.config["beagleboneblue"]["motor"]["position"]["front_right"]
        self.motor_back_left = self.config["beagleboneblue"]["motor"]["position"]["back_left"]
        self.motor_back_right = self.config["beagleboneblue"]["motor"]["position"]["back_right"]
        self.grab = True
        self.echo = "P9_23"
        self.echo = self.config["beagleboneblue"]["hcsr04"]["echo"]
        self.trigger = "GPIO1_25"
        self.trigger = self.config["beagleboneblue"]["hcsr04"]["trigger"]
        self.servo_claw = 8
        self.servo_claw = self.config["beagleboneblue"]["claw"]["servo"]
        self.servo_claw_angle_open = -45.0
        self.servo_claw_angle_open = self.config["beagleboneblue"]["claw"]["angle_open"]
        self.servo_claw_angle_close = 45.0
        self.servo_claw_angle_close = self.config["beagleboneblue"]["claw"]["angle_close"]

        # Boot
        # Configuration
        GPIO.setup(self.trigger, GPIO.OUT)  # Trigger
        GPIO.setup(self.echo, GPIO.IN)  # Echo
        GPIO.output(self.trigger, False)

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

    def claw_toggle(self, quiet=False):
        if self.grab:
            self.claw_close(quiet)
        else:
            self.claw_open(quiet)

    def claw(self, quiet=False):
        return self.claw_toggle(quiet)

    def claw_open(self, quiet=False):
        self.print_stdout("claw_open()", quiet)
        self.grab = True
        self.set_servo(self.servo_claw, self.servo_claw_angle_open, quiet=True)

    def claw_close(self, quiet=False):
        self.print_stdout("claw_close()", quiet)
        self.grab = False
        self.set_servo(self.servo_claw, self.servo_claw_angle_close, quiet=True)

    def read_distance(self, quiet=False):
        distance = 0
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

    def move(self, period=1, duty=1, quiet=False):
        self.print_stdout("move(period={}, duty={})".format(period, duty), quiet)
        for i in range(1, 5):
            self.set_motor(i, duty * self.duty_ratio[i-1], quiet=True)
        self.sleep(period, quiet=True)
        for i in range(1, 5):
            self.set_motor(i, 0, quiet=True)

    def move_forward(self, blocks=1, speed=-1, quiet=False):
        if speed < 0:
            speed = self.duty
        self.print_stdout("move_forward(blocks={}, speed={})".format(blocks, speed), quiet)
        period = blocks * self.block_length / speed
        self.move(period, speed, quiet=True)

    def move_backwards(self, blocks=1, speed=-1, quiet=False):
        if speed < 0:
            speed = self.duty
        self.print_stdout("move_backwards(blocks={}, speed={})".format(blocks, speed), quiet)
        period = blocks * self.block_length / speed
        self.move(period, speed*-1, quiet=True)

    def turn_right(self, angle=90, quiet=False):
        self.print_stdout("turn_right(angle={})".format(angle), quiet)

        duty = 0.3  # Use fixed duty cycle for turning

        # Left
        self.set_motor(self.motor_front_left, duty, quiet=True)
        self.set_motor(self.motor_back_left, duty, quiet=True)
        # Right
        self.set_motor(self.motor_front_right, duty*-1, quiet=True)
        self.set_motor(self.motor_back_right, duty*-1, quiet=True)

        self.sleep(angle * self.turn_right_period, quiet=True)

        self.set_motor(self.motor_front_left, 0, quiet=True)
        self.set_motor(self.motor_back_left, 0, quiet=True)
        self.set_motor(self.motor_front_right, 0, quiet=True)
        self.set_motor(self.motor_back_right, 0, quiet=True)

    def turn_left(self, angle=90, quiet=False):
        self.print_stdout("turn_left(angle={})".format(angle), quiet)

        duty = 0.3  # Use fixed duty cycle for turning

        # Left
        self.set_motor(self.motor_front_left, duty*-1, quiet=True)
        self.set_motor(self.motor_back_left, duty*-1, quiet=True)
        # Right
        self.set_motor(self.motor_front_right, duty, quiet=True)
        self.set_motor(self.motor_back_right, duty, quiet=True)

        self.sleep(angle * self.turn_left_period, quiet=True)

        self.set_motor(self.motor_front_left, 0, quiet=True)
        self.set_motor(self.motor_back_left, 0, quiet=True)
        self.set_motor(self.motor_front_right, 0, quiet=True)
        self.set_motor(self.motor_back_right, 0, quiet=True)

    def say_welcome(self, quiet=False):
        self.print_stdout("say_welcome()", quiet)
        self.say_yes(True)
        message = "Welcome to BluPants! My name is {} robot. Are you ready for learning Computer Science with me? " \
                  "Visit blupants.org to get started.".format(self.name)
        self.say(message, quiet)

    def say(self, message, quiet=False):
        self.print_stdout(message, quiet)
        if not quiet and self.enable_tts:
            try:
                self.tts_engine.say(message)
                self.tts_engine.runAndWait()
            except:
                pass


class BluPants6DOF(BluPants):
    def __init__(self):
        super().__init__()
        self.base_servo_index = -1
        self.arm_rest_pos = {}
        self.arm_ready_pos = {}
        self.reload()

    def reload(self):
        super().reload()
        self.servo_claw_angle_open = 0
        self.servo_claw_angle_open = self.config["beagleboneblue"]["claw"]["angle_open"]
        self.servo_claw_angle_close = 60.0
        self.servo_claw_angle_close = self.config["beagleboneblue"]["claw"]["angle_close"]
        self.grab = True

        rest_ang = self.config.get("beagleboneblue", {}).get("servo", {}).get("init_angle", [0, 0, 0, 15, -90, 90, 0, 0])

        self.base_servo_index = self.servo_claw - 5
        self.arm_rest_pos = {}
        # i   Description                        pin/rail/s
        # 1   camera servo_horizontal            0
        # 2   camera servo_vertical              1
        # 3   base servo (left/right)            2
        # 4   lower joint                        3
        # 5   upper base joint                   4
        # 6   claw joint                         5
        # 7   claw spin                          6
        # 8   claw open/close (self.servo_claw)  7
        for i in range(self.base_servo_index, self.servo_claw + 1):
            self.arm_rest_pos[str(i)] = {"angle": rest_ang[i-1], "step": 10}

        lower_joint = "4"
        self.arm_ready_pos = json.loads(json.dumps(self.arm_rest_pos))
        self.arm_ready_pos[lower_joint]["angle"] = -60

    def _is_equal_current_pos(self, pos):
        for i in pos:
            s = int(i)-1
            conf = pos[i]
            cur = self.cur_angles[s]
            conf_pos = conf.get("angle", -1)
            if int(cur) != int(conf_pos):
                return False
        return True

    def _move_servos_pos(self, pos):
        s = int(pos["servo"])
        i = int(self.cur_angles[s-1])
        e = int(pos["angle"])
        step = int(pos["step"])
        if i > e:
            step = step * -1
        for i in range(i, e, step):
            self.set_servo(s, i)
        self.set_servo(s, e)

    def get_servos_pos(self, pos_name=None, fmt="array"):
        pos = self.cur_angles
        if pos_name:
            if str(pos_name).lower().find("ready") != -1:
                if fmt.lower() == "json".lower():
                    return self.arm_ready_pos
                else:
                    pos = []
                    for i in range(1, 9):
                        pos.append(self.arm_ready_pos.get(str(i), {}).get("angle", 0))

            if str(pos_name).lower().find("rest") != -1:
                if fmt.lower() == "json".lower():
                    return self.arm_rest_pos
                else:
                    pos = []
                    for i in range(1, 9):
                        pos.append(self.arm_rest_pos.get(str(i), {}).get("angle", 0))
        else:
            if fmt.lower()=="json".lower():
                result = {}
                for s,ang in enumerate(pos):
                    result[s] =  {"angle": ang, "step": 10}
                pos = result
        return pos

    def move_arm(self, pos):
        from multiprocessing.dummy import Pool as ThreadPool

        pos_array = []
        for s in pos:
            item = pos[s]
            item["servo"] = s
            pos_array.append(item)

        # Make the Pool of workers
        n_workers = len(pos_array)
        pool = ThreadPool(n_workers)

        # Move servos in their own threads
        # and return the results
        results = pool.map(self._move_servos_pos, pos_array)

        # Close the pool and wait for the work to finish
        pool.close()
        pool.join()

        return results

    def move(self, period=1, duty=1, quiet=False):
        self.print_stdout("move(period={}, duty={})".format(period, duty), quiet)

        # Arm cannot "move forward" at the "arm_ready_pos"
        if self._is_equal_current_pos(self.arm_ready_pos):
            self.move_arm(self.arm_rest_pos)

        step = duty * 10
        if step < 0:
            step *= -1
            period *= -1
        i = self.base_servo_index
        pos = {
            i+1: {"angle": self.cur_angles[i] + (period*10), "step": step},
            i+2: {"angle": self.cur_angles[i+1] + (period*10), "step": step},
            i+3: {"angle": self.cur_angles[i+2] - (period*10), "step": step},
        }
        self.move_arm(pos)

    def nod(self, quick=False):
        self.claw_toggle()
        self.claw_toggle()
        if quick:
            return
        self.set_servo(7, 90)
        self.set_servo(7, -90)
        self.set_servo(7, 0)
        self.claw_toggle()
        self.claw_toggle()

    def say_yes(self, quiet=False):
        self.print_stdout("say_yes()", quiet)
        self.say("Yes!", quiet)
        self.nod()

    def say_no(self, quiet=False):
        self.print_stdout("say_no()", quiet)
        self.say("No!", quiet)
        self.nod(True)


    def turn_right(self, angle=90, quiet=False):
        self.print_stdout("turn_right(angle={})".format(angle), quiet)
        if angle > 0:
            angle = angle * -1
        self.set_servo(3, angle)

    def turn_left(self, angle=90, quiet=False):
        self.print_stdout("turn_left(angle={})".format(angle), quiet)
        if angle < 0:
            angle = angle * -1
        self.set_servo(3, angle)

    def shutdown(self, quiet=False):
        self.nod(True)
        self.move_arm(self.arm_rest_pos)
        time.sleep(2)
        super().shutdown(quiet)


class BluPantsCar(BluPants):
    def __init__(self):
        super().__init__()
        self.reload()

    def reload(self):
        super().reload()
        self.servo_horizontal = 1
        self.servo_horizontal = self.config["beagleboneblue"]["camera"]["servo_horizontal"]
        self.servo_vertical = 2
        self.servo_vertical = self.config["beagleboneblue"]["camera"]["servo_vertical"]

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
        position = angle * self.servo_angle_factor
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


class EduMIP(BluPants):
    def __init__(self):
        super().__init__()
        self.reload()

    def reload(self):
        super().reload()

        self.block_length = 0.28
        self.block_length = self.config["EduMIP"]["block_length"]
        self.turn_coefficient = 0.0175
        self.turn_coefficient = self.config["EduMIP"]["turn_coefficient"]
        self.meter_coefficient = 14
        self.meter_coefficient = self.config["EduMIP"]["meter_coefficient"]
        self.servo_shoulder_left = 7
        self.servo_shoulder_left = self.config["EduMIP"]["servo_shoulder_left"]
        self.servo_shoulder_right = 6
        self.servo_shoulder_right = self.config["EduMIP"]["servo_shoulder_right"]
        self.servo_claw_angle_open = 45.0
        self.servo_claw_angle_open = self.config["EduMIP"]["claw"]["angle_open"]
        self.servo_claw_angle_close = 30.0
        self.servo_claw_angle_close = self.config["EduMIP"]["claw"]["angle_close"]
        self.var_dir = "/tmp/blupants/"
        print("Make sure you have eduMPI balanced before running this script.")
        print("#rc_balance_dstr -i dstr")

    def _create_cmd_file(self, cmd):
        file_path = os.path.join(self.var_dir, cmd)
        open(file_path, 'a').close()

    def move(self, distance_meter=1.0, quiet=False):
        self.print_stdout("move(distance_meter={})".format(distance_meter), quiet)
        if distance_meter > 0:
            self._create_cmd_file("up.txt.")
        else:
            self._create_cmd_file("down.txt.")
            distance_meter *= -1
        self.sleep(self.meter_coefficient * distance_meter, quiet=True)
        self._create_cmd_file("break.txt.")
        self.sleep(2, quiet=True)

    def move_forward(self, blocks=1, speed=-1, quiet=False):
        if speed < 0:
            speed = self.duty
        self.print_stdout("move_forward(blocks={})".format(blocks), quiet)
        self.move(self.block_length*blocks*self.block_length, quiet=True)

    def move_backwards(self, blocks=1, speed=-1, quiet=False):
        if speed < 0:
            speed = self.duty
        self.print_stdout("move_backwards(blocks={})".format(blocks), quiet)
        self.move(self.block_length*blocks*-1*self.block_length, quiet=True)

    def turn_left(self, angle=90.0, quiet=False):
        self.print_stdout("turn_left(angle={})".format(angle), quiet)
        self._create_cmd_file("left.txt.")
        self.sleep(self.turn_coefficient * angle, quiet=True)
        self._create_cmd_file("break.txt.")
        self.sleep(2, quiet=True)

    def turn_right(self, angle=90.0, quiet=False):
        self.print_stdout("turn_right(angle={})".format(angle), quiet)
        self._create_cmd_file("right.txt.")
        self.sleep(self.turn_coefficient * angle, quiet=True)
        self._create_cmd_file("break.txt.")
        self.sleep(2, quiet=True)

    def claw_open(self, quiet=False):
        self.print_stdout("claw_open()", quiet)
        self.grab = True
        self.set_servo(self.servo_shoulder_left, self.servo_claw_angle_open * -1, quiet=True)
        self.set_servo(self.servo_shoulder_right, self.servo_claw_angle_open, quiet=True)

    def claw_close(self, quiet=False):
        self.print_stdout("claw_close()", quiet)
        self.grab = False
        self.set_servo(self.servo_shoulder_left, self.servo_claw_angle_close, quiet=True)
        self.set_servo(self.servo_shoulder_right, self.servo_claw_angle_close * -1, quiet=True)

    def say_no(self, quiet=False):
        self.print_stdout("say_no()", quiet)
        self.say("No!", quiet)
        self.set_servo(self.servo_shoulder_left, 0, quiet=True)
        self.set_servo(self.servo_shoulder_right, 0, quiet=True)
        self.sleep(0.2, quiet=True)
        self.set_servo(self.servo_shoulder_right, -45, quiet=True)
        self.set_servo(self.servo_shoulder_left, -45, quiet=True)
        self.sleep(0.2, quiet=True)
        self.set_servo(self.servo_shoulder_left, 45, quiet=True)
        self.set_servo(self.servo_shoulder_right, 45, quiet=True)
        self.sleep(0.2, quiet=True)
        self.set_servo(self.servo_shoulder_right, 0, quiet=True)
        self.set_servo(self.servo_shoulder_left, 0, quiet=True)

    def say_yes(self, quiet=False):
        self.print_stdout("say_yes()", quiet)
        self.say("Yes!", quiet)
        self.set_servo(self.servo_shoulder_left, 0, quiet=True)
        self.set_servo(self.servo_shoulder_right, 0, quiet=True)
        self.sleep(0.2, quiet=True)
        self.set_servo(self.servo_shoulder_right, 80, quiet=True)
        self.set_servo(self.servo_shoulder_left, -80, quiet=True)
        self.sleep(0.2, quiet=True)
        self.set_servo(self.servo_shoulder_left, 80, quiet=True)
        self.set_servo(self.servo_shoulder_right, -80, quiet=True)
        self.sleep(0., quiet=True)
        self.set_servo(self.servo_shoulder_right, 0, quiet=True)
        self.set_servo(self.servo_shoulder_left, 0, quiet=True)


#r = BluPants6DOF()

# ap = r.get_servos_pos()
# print(ap)
# ap = r.get_servos_pos(fmt="json")
# print(ap)
# ap = r.get_servos_pos("arm_ready_pos")
# print(ap)
# ap = r.get_servos_pos("arm_ready_pos", fmt="json")
# print(ap)
# ap = r.get_servos_pos("arm_rest_pos")
# print(ap)
# ap = r.get_servos_pos("arm_rest_pos", fmt="json")
# print(ap)

# r.move_arm(r.arm_ready_pos)
# r.say_yes()
# d = r.read_distance()
# r.turn_left()
# r.say_no()
# r.turn_left(0)
#
# r.move_forward(2)
# r.turn_right(45)
# r.claw_toggle()
# r.move_forward(2)
# r.turn_left(45)
# r.claw_toggle()
# r.move_backwards(3)
# r.turn_right(60)
# r.move_forward(1)

#r.shutdown()