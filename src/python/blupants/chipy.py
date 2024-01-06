import turtle
import time


try:
    import robots_common
except:
    import blupants.robots_common as robots_common


class ChiPy(robots_common.RobotHollow):
    def __init__(self):
        super().__init__()
        self.running = False
        self.reload()
        self.turtle = turtle.Turtle()
        self.running = True

    def reload(self):
        super().reload()

        self.name = "ChiPy"
        self.duty = self.config["duty"]
        self.block_length = self.config["block_length"]

    def shutdown(self, quiet=False):
        self.print_stdout("shutdown(quiet={})".format(quiet), quiet)
        time.sleep(5)
        self.turtle.hideturtle()
        self.turtle.clear()
        self.running = False

    def sleep(self, seconds=1.0, quiet=False):
        self.print_stdout("sleep(seconds={})".format(seconds), quiet)
        time.sleep(seconds)

    def move_forward(self, blocks=1, speed=-1, quiet=False):
        self.print_stdout("move_forward(blocks={}, speed={})".format(blocks, speed), quiet)
        self.turtle.forward(blocks * self.block_length)
        time.sleep(0.5)

    def move_backwards(self, blocks=1, speed=-1, quiet=False):
        self.print_stdout("move_backwards(blocks={}, speed={})".format(blocks, speed), quiet)
        self.turtle.back(blocks * self.block_length)
        time.sleep(0.5)

    def turn_right(self, angle=90, quiet=False):
        self.print_stdout("turn_right(angle={})".format(angle), quiet)
        self.turtle.right(angle)
        time.sleep(0.5)

    def turn_left(self, angle=90, quiet=False):
        self.print_stdout("turn_left(angle={})".format(angle), quiet)
        self.turtle.left(angle)
        time.sleep(0.5)

    def say_yes(self, quiet=False):
        self.print_stdout("say_yes()", quiet)
        self.say("Yes!")
        time.sleep(0.5)

    def say_no(self, quiet=False):
        self.print_stdout("say_no()", quiet)
        self.say("No!")
        time.sleep(0.5)

    def say_welcome(self, quiet=False):
        self.print_stdout("say_welcome()", quiet)
        message = f"Welcome to BluPants! My name is {self.name} robot."
        self.say(message, quiet)

    def say(self, message, quiet=False):
        self.turtle.write(message, quiet)


def test():
    r = ChiPy()
    print("Testing...")

    robot = r
    robot.move_forward(2)
    robot.move_backwards(1)
    robot.turn_left(90)
    robot.move_forward(2)
    robot.turn_right(30)
    robot.move_backwards(1)
    time.sleep(1)

    d = robot.read_distance()
    print(d)

    robot.move_forward(2)
    robot.say_yes()
    robot.move_forward(2)
    robot.say("Done testing!")
    robot.move_forward(2)

    robot.shutdown()

# test()
