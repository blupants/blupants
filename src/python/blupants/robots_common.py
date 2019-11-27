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
    def __init__(self):
        self.buffer = []

    def get_stdout(self):
        data = ""
        for message in self.buffer:
            data += message + "\n"
        return data + "\n"

    def print(self, message):
        print(message)
        if len(self.buffer) >= 6:
            self.buffer = self.buffer[1:]
        self.buffer.append("data:" + str(message))


class RobotHollow:
    def __init__(self, platform):
        self._robot = None

    def claw_toggle(self):
        pass

    def claw_open(self):
        pass

    def claw_close(self):
        pass

    def read_distance(self):
        return -10

    def move_forward(self, blocks=1, speed=0.5):
        pass

    def move_backwards(self, blocks=1, speed=0.5):
        pass

    def turn_right(self, angle=90):
        pass

    def turn_left(self, angle=90):
        pass

    def shutdown(self):
        pass
