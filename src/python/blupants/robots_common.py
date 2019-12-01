import os

global default_config
default_config =\
    {
        "name": "BluPants",
        "measurement_system": "m",
        "step_distance": 0.3,
        "period": 0.02,
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
                        "turn_right_period": 0.0053,
                        "turn_left_period": 0.0052
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

    def get_stdout(self):
        return self.standard_output.get_stdout()

    def print_stdout(self, message, quiet=False):
        if not quiet:
            self.standard_output.print(message)

    def print(self, message, quiet=False):
        self.say(message, quiet)

    def say_yes(self, quiet=False):
        self.say("yes", quiet)

    def say_no(self, quiet=False):
        self.say("no", quiet)

    def say_welcome(self, quiet=False):
        self.say_yes(quiet)

    def say(self, message, quiet=False):
        self.print_stdout(message, quiet)
        pass

    def _warning(self):
        self.print_stdout("RobotHollow: Method not implemented!")

    def claw_toggle(self):
        self._warning()
        pass

    def claw_open(self):
        self._warning()
        pass

    def claw_close(self):
        self._warning()
        pass

    def read_distance(self):
        self._warning()
        return -10

    def move_forward(self, blocks=1, speed=0.5):
        self._warning()
        pass

    def move_backwards(self, blocks=1, speed=0.5):
        self._warning()
        pass

    def turn_right(self, angle=90):
        self._warning()
        pass

    def turn_left(self, angle=90):
        self._warning()
        pass

    def sleep(self, seconds=1.0):
        self._warning()
        pass

    def shutdown(self, quiet=False):
        self._warning()
        pass

    def set_servo(self, i=1, angle=0.0):
        self._warning()
        pass

    def set_motor(self, i=1, duty=0.5):
        self._warning()
        pass

    def move(self, period=1, duty=1):
        self._warning()
        pass

    def camera_toggle(self):
        self._warning()
        pass

    def look_angle(self, angle=90):
        self._warning()
        pass

    def say_yes(self):
        self._warning()
        pass

    def say_no(self):
        self._warning()
        pass

    def say_welcome(self, quiet=False):
        self._warning()
        pass

    def say(self, message, quiet=False):
        self._warning()
        pass
