import os
import json

global default_config
default_config =\
    {
        "robot_id": 0,
        "name": "BluPants",
        "use_opencv": False,
        "measurement_system": "m",
        "step_distance": 0.3,
        "period": 0.02,
        "tts_all_commands": False,
        "blupants":
            {
                "claw":
                    {
                        "servo": 8,
                        "angle_open": -45.0,
                        "angle_close": 45.0
                    },
                "hcsr04":
                    {
                        "echo": "P9_23",
                        "trigger": "GPIO1_25",
                        "vcc": "GP0_3v3",
                        "gnd": "GP0_GND"
                    },
                "motor":
                    {
                        "position":
                            {
                                "front_left": 1,
                                "front_right": 2,
                                "back_left": 3,
                                "back_right": 4
                            },
                        "duty_ratio": [1.0, 1.0, 1.0, 1.0],
                        "turn_right_period": 0.005,
                        "turn_left_period": 0.005
                    },
                "camera":
                    {
                        "servo_horizontal": 1,
                        "servo_vertical": 2
                    }
            },
        "EduMIP":
            {
                "block_length": 0.28,
                "turn_coefficient": 0.0175,
                "meter_coefficient": 14,
                "servo_shoulder_left": 7,
                "servo_shoulder_right": 6,
                "claw":
                    {
                        "angle_open": 45.0,
                        "angle_close": 30.0
                    },
            }
}


global config_file
config_file = "/root/blupants.json"


if os.path.isfile(config_file):
    with open(config_file) as f:
        try:
            default_config = json.load(f)
            print(default_config)
        except:
            pass

class StudioConsole:
    # Singleton instance.
    _instance = None

    # Singleton Implementation
    class __StudioConsole:
        def __init__(self):
            self.standard_output_mem_file = "/tmp/blupants/standard_output_mem_file"
            self.standard_output_buffer = []

        def get_stdout(self):
            data = ""
            for message in self.standard_output_buffer:
                data += message + "\n"

            if len(data) == 0:
                lines = []
                with open(self.standard_output_mem_file, "r") as f:
                    lines = f.readlines()
                data = "".join(lines)

            return data + "\n"

        def print(self, message):
            print(message)
            if len(self.standard_output_buffer) >= 6:
                self.standard_output_buffer = self.standard_output_buffer[1:]
            self.standard_output_buffer.append("data:" + str(message))
            try:
                with open(self.standard_output_mem_file, "w") as f:
                    for message in self.standard_output_buffer:
                        f.writelines(message + "\n")
                    f.writelines("\n")
            except:
                pass

        def clear(self):
            self.standard_output_buffer.clear()
            os.system("echo \"\" > {}".format(self.standard_output_mem_file))

    def __init__(self):
        if not self._instance:
            self._instance = StudioConsole.__StudioConsole()

    def get_stdout(self):
        return self._instance.get_stdout()

    def print(self, message):
        self._instance.print(message)

    def clear(self):
        self._instance.clear()


def get_stdout():
    std_out = StudioConsole()
    return std_out.get_stdout()


class RobotHollow:
    def __init__(self):
        self.standard_output = StudioConsole()

    def _warning(self, name=""):
        self.print_stdout("RobotHollow: Method {} not implemented!".format(name))

    def get_stdout(self):
        return self.standard_output.get_stdout()

    def print_stdout(self, message, quiet=False):
        if not quiet:
            self.standard_output.print(message)

    def print(self, message, quiet=False):
        try:
            self.say(message, quiet)
        except:
            self._warning("print")

    def say_yes(self, quiet=False):
        try:
            self.say("yes", quiet)
        except:
            self._warning("say_yes")

    def say_no(self, quiet=False):
        try:
            self.say("no", quiet)
        except:
            self._warning("say_no")

    def say_welcome(self, quiet=False):
        try:
            self.say_yes(quiet)
        except:
            self._warning("say_welcome")

    def say(self, message, quiet=False):
        self.print_stdout(message, quiet)

    def claw_toggle(self):
        self._warning("claw_toggle")

    def claw_open(self):
        self._warning("claw_open")

    def claw_close(self):
        self._warning("claw_close")

    def read_distance(self):
        self._warning("read_distance")
        return -10

    def move_forward(self, blocks=1, speed=0.5):
        self._warning("move_forward")
        pass

    def move_backwards(self, blocks=1, speed=0.5):
        self._warning("move_backwards")

    def turn_right(self, angle=90):
        self._warning("turn_right")

    def turn_left(self, angle=90):
        self._warning("turn_left")

    def sleep(self, seconds=1.0):
        self._warning("sleep")

    def shutdown(self, quiet=False):
        self._warning("shutdown")

    def set_servo(self, i=1, angle=0.0):
        self._warning("set_servo")

    def set_motor(self, i=1, duty=0.5):
        self._warning("set_motor")

    def move(self, period=1, duty=1):
        self._warning("move")

    def camera_toggle(self):
        self._warning("camera_toggle")

    def look_angle(self, angle=90):
        self._warning("look_angle")
