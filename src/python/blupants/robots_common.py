import os
import json

global config_file
config_file = "/root/blupants.json"
if not os.path.isfile(config_file):
    config_file = "/etc/blupants.json"
    if not os.path.isfile(config_file):
        install_path = os.path.dirname(os.path.abspath(__file__))
        config_file = install_path + "/blupants.json"


if os.path.isfile(config_file):
    with open(config_file) as f:
        try:
            default_config = json.load(f)
            print(default_config)
        except:
            pass


class RobotConfig:
    _default_config = {}
    config = {}

    def __init__(self):
        install_path = os.path.dirname(os.path.abspath(__file__))
        default_config_file = install_path + "/blupants.json"
        if os.path.isfile(default_config_file):
            with open(default_config_file) as f:
                try:
                    self._default_config = json.load(f)
                except Exception as e:
                    print(e.message)

        if os.path.isfile(config_file):
            with open(config_file) as f:
                try:
                    self.config = json.load(f)
                except:
                    pass

        for key in self._default_config:
            obj0 = self._default_config[key]
            if key not in self.config:
                self.config[key] = obj0
            if isinstance(obj0, dict):
                for key1 in obj0:
                    obj1 = obj0[key1]
                    if key1 not in self.config[key]:
                        self.config[key][key1] = obj1
                    if isinstance(obj1, dict):
                        for key2 in obj1:
                            obj2 = obj1[key2]
                            if key2 not in self.config[key][key1]:
                                self.config[key][key1][key2] = obj2
                            if isinstance(obj2, dict):
                                for key3 in obj2:
                                    obj3 = obj2[key3]
                                    if key3 not in self.config[key][key1][key2]:
                                        self.config[key][key1][key2][key3] = obj3
                                    if isinstance(obj3, dict):
                                        for key4 in obj3:
                                            obj4 = obj3[key4]
                                            if key4 not in self.config[key][key1][key2][key3]:
                                                self.config[key][key1][key2][key3][key4] = obj4

        self.camera_pos = 0
        self.camera_toggle_positions = [
            [-89.0, 0], [89.0, 0], [89.0, 30.0], [0, 30.0], [-89.0, 30.0], [-89.0, 0], [-89.0, -30.0], [0, -30.0],
            [89.0, -30.0], [89.0, 0], [0, 0]
        ]


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
    _robot_config_obj = RobotConfig()
    config = _robot_config_obj.config

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
        self.print_stdout(message, quiet)

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
        self.print(message, quiet)

    def claw_toggle(self):
        self._warning("claw_toggle")

    def claw_open(self):
        self._warning("claw_open")

    def claw_close(self):
        self._warning("claw_close")

    def read_distance(self):
        self._warning("read_distance")
        return -10

    def move_forward(self, blocks=1, speed=-1):
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

