"""BluPants Robot class.

This module provides a factory so you can instantiate robots from
any hardware supported by BluPants. Currently supported platforms are:

* Beaglebone Blue: "blupants_car" or "edumip" - Ex:
robot = robots.Robot("blupants_car")

* Beaglebone Black: "beagleboneblack" - Ex:
robot = robots.Robot("beagleboneblack")

* RaspberryPi: "raspberrypi" - Ex:
robot = robots.Robot("raspberrypi")

* Lego Ev3: "gripper" or "ev3" - Ex:
robot = robots.Robot("gripper")

After instantiating your robot, you can call all the functions available at
the BluPants IDE <http://blupants.org>. For instance, you can call methods
such as: move_forward(), turn_right(), read_distance(), claw_close(). See
usage bellow for examples.

Typical usage:

    >>> import blupants.robots_common as robots_common
    >>> import blupants.robots as robots

    # instantiate a Beaglebone Blue gripper/claw robot
    >>> robot = robots.Robot("blupants_car")

    # instantiate a RaspberryPi gripper/claw robot
    >>> robot = robots.Robot("raspberrypi")

    # instantiate a Lego Ev3 Gripp3r robot
    >>> robot = robots.Robot("gripper")

    # move robot one block forward
    >>> robot.move_forward()

    # move robot two blocks forward
    >>> robot.move_forward(2)

    # turn robot left 90 degrees
    >>> robot.turn_left()

    # turn robot right 30 degrees
    >>> robot.turn_right(30)

    # read the distance from the nearest obstacle in front of the robot
    >>> d = robot.read_distance()
    Distance: [25] cm.

    # close the robot claw
    >>> robot.claw_close()

    # robot text-to-speech
    >>> robot.say("Hello from BluPants.")
    Hello from BluPants.
"""

try:
    import robots_common
except:
    import blupants.robots_common as robots_common

__author__ = 'BluPants <blupants.robot@gmail.com>'


class RobotFactory:
    """Constructs the robots according to the proper platform.
    """
    def __init__(self):
        """Create an empty list of supported platforms
        """
        self._creators = {}

    def register_robot(self, platform, creator):
        """
        register_robot(platform, creator)

        Add a robot platform to the supported list, with its respective class.
        """
        self._creators[platform] = creator

    def get_robot(self, platform):
        """
        get_robot(platform)

        Factory method that constructs the robot according to the class that
        implements it.
        """
        creator = self._creators.get(platform)
        if not creator:
            return robots_common.RobotHollow()
        return creator()


class Robot(robots_common.RobotHollow):
    """Instances of the Robot class represent a robot platform that implements
    the interface RobotHollow.
    """
    def __init__(self, platform):
        """Create a robot based on the platform provided. The platforms
        currently supported are:

        Robot("blupants_car")
        Robot("edumip")
        Robot("beagleboneblack")
        Robot("raspberrypi")
        Robot("gripper")
        Robot("ev3")
        """
        self._robot = factory.get_robot(platform)

    def reload(self):
        """
        reload()

        Reload robot configuration.
        """
        self._robot.reload()

    def print(self, message):
        """
        print(message)

        Print the input message to the standard output.
        """
        return self._robot.print(message)

    def claw_toggle(self):
        """
        claw_toggle()

        If the claw is closed, it calls claw_open().
        If the claw is open, it call claw_close().
        """
        return self._robot.claw_toggle()

    def claw_open(self):
        """
        claw_open()

        Open the robot claw.
        """
        return self._robot.claw_open()

    def claw_close(self):
        """
        claw_close()

        Close the robot claw.
        """
        return self._robot.claw_close()

    def read_distance(self):
        """
        read_distance()

        Return the distance in centimeters of the closest obstacle in front of the robot.
        """
        return self._robot.read_distance()

    def move_forward(self, blocks=1, speed=-1):
        """
        move_forward(blocks, speed)

        Move the robot forward using the number of the blocks and the speed provided.
        Speed ranges from 0 (stopped) to 1 (maximum speed).
        """
        return self._robot.move_forward(blocks, speed)

    def move_backwards(self, blocks=1, speed=-1):
        """
        move_backwards(blocks, speed)

        Move the robot backwards using the number of the blocks and the speed provided.
        Speed ranges from 0 (stopped) to 1 (maximum speed).
        """
        return self._robot.move_backwards(blocks, speed)

    def turn_right(self, angle=90):
        """
        turn_right(angle)

        Turn the robot right using the angle provided as input.
        If no angle is provided, the robot turns 90 degrees (default value).
        """
        return self._robot.turn_right(angle)

    def turn_left(self, angle=90):
        """
        turn_left(angle)

        Turn the robot left using the angle provided as input.
        If no angle is provided, the robot turns 90 degrees (default value).
        """
        return self._robot.turn_left(angle)

    def sleep(self, seconds=1.0):
        """
        sleep(seconds)

        Pause the robot execution for the number of seconds provided.
        If no value is provided as inputs, the robot sleeps for 1 second.
        """
        return self._robot.sleep(seconds)

    def shutdown(self, quiet=False):
        """
        shutdown(quiet)

        Safely shutdown robot peripherals after code execution is finished.
        """
        return self._robot.shutdown(quiet)

    def set_servo(self, i=1, angle=0.0):
        """
        set_servo(i, angle)

        Set servo with index i to the angle provided as input.
        Angle ranges from -90.0 to 90.0 degrees.
        """
        return self._robot.set_servo(i, angle)

    def set_motor(self, i=1, duty=0.5):
        """
        set_motor(i, duty)

        Set motor with index i to the duty cycle provided as input.
        Duty cycle ranges from 0.0 to 1.0.
        """
        return self._robot.set_motor(i, duty)

    def move(self, period=1, duty=1):
        """
        move(period, duty)

        Set all motors to the duty provided as input. All motors stop after the period
        of seconds provided as input.
        """
        return self._robot.move(period, duty)

    def camera_toggle(self):
        """
        camera_toggle()

        Move camera to the next preset position.

        The preset position sequence is:
        [-89.0, 0], [89.0, 0], [89.0, 30.0], [0, 30.0], [-89.0, 30.0],
        [-89.0, 0], [-89.0, -30.0], [0, -30.0], [89.0, -30.0], [89.0, 0], [0, 0]

        The tuple [X,Y] represents the camera position.
        X: angle for the horizontal servo (pan)
        Y: angle for the vertical servo (tilt).
        """
        return self._robot.camera_toggle()

    def look_angle(self, angle=90):
        """
        look_angle(angle)

        Set the camera horizontal position (pan) to the angle provided as input and
        reset the vertical position (tilt) to zero.
        Camera pos: [angle, 0].
        """
        return self._robot.look_angle(angle)

    def say_yes(self):
        """
        say_yes()

        Robot nods camera servos and say "Yes!" using the TTS (Text-To-Speech) module.
        """
        return self._robot.say_yes()

    def say_no(self):
        """
        say_no()

        Robot shakes camera servos and say "No!" using the TTS (Text-To-Speech) module.
        """
        return self._robot.say_no()

    def say_welcome(self):
        """
        say_welcome()

        Robot introduces itself telling its name and invites us to learn Computer Science.
        """
        return self._robot.say_welcome()

    def say(self, message):
        """
        say(message)

        Print the message provided as input and say it using the TTS (Text-To-Speech) module.
        """
        return self._robot.say(message)


global factory
factory = RobotFactory()

try:
    import beagleboneblue
except:
    try:
        import blupants.beagleboneblue as beagleboneblue
    except:
        pass
try:
    factory.register_robot("generic", beagleboneblue.BeagleBoneBlue)
except:
    pass
try:
    factory.register_robot("blupants_car", beagleboneblue.BluPantsCar)
except:
    pass
try:
    factory.register_robot("edumip", beagleboneblue.EduMIP)
except:
    pass
try:
    factory.register_robot("beagleboneblue_6dof_claw", beagleboneblue.BluPants6DOF)
except:
    pass

try:
    import raspberrypi
except:
    try:
        import blupants.raspberrypi as raspberrypi
    except:
        pass
try:
    factory.register_robot("generic", raspberrypi.RaspberryPi)
    factory.register_robot("raspberrypi", raspberrypi.RaspberryPi)
    factory.register_robot("pi", raspberrypi.RaspberryPi)
except:
    pass

try:
    import beagleboneblack
except:
    try:
        import blupants.beagleboneblack as beagleboneblack
    except:
        pass
try:
    factory.register_robot("generic", beagleboneblack.BeagleBoneBlack)
    factory.register_robot("beagleboneblack", beagleboneblack.BeagleBoneBlack)
    factory.register_robot("black", beagleboneblack.BeagleBoneBlack)
except:
    pass

try:
    import ev3
except:
    try:
        import blupants.ev3 as ev3
    except:
        pass
try:
    factory.register_robot("generic", ev3.ev3)
except:
    pass
try:
    factory.register_robot("gripp3r", ev3.Gripp3r)
    factory.register_robot("gripper", ev3.Gripp3r)
except:
    pass

try:
    import alphabot2
except:
    try:
        import blupants.alphabot2 as alphabot2
    except:
        pass
try:
    factory.register_robot("alphabot", alphabot2.AlphaBot2)
    factory.register_robot("alphabot2", alphabot2.AlphaBot2)
except:
    pass