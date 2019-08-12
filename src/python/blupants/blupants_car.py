import rcpy
import rcpy.motor as motor
import rcpy.servo as servo
import rcpy.clock as clock
import rcpy.gpio as gpio
from rcpy.gpio import InputEvent
import Adafruit_BBIO.GPIO as GPIO

import time
import random

GPIO.cleanup()


#0
#unused
#1
#unused
#2
echo = "P9_23" #echo = "GPIO1_17" # resitor yellow
#3
trigger = "GPIO1_25"  # direct white
#4
vcc = "GP0_3v3"       # direct blue
#5
gnd = "GP0_GND"       # direct green


GPIO.cleanup()


#Configuration
print("trigger: [{}]".format(trigger))
GPIO.setup(trigger,GPIO.OUT) #Trigger
print("echo: [{}]".format(echo))
GPIO.setup(echo,GPIO.IN)  #Echo
GPIO.output(trigger, False)
print("Setup completed!")

#Security
GPIO.output(trigger, False)
time.sleep(0.5)
TRIG = trigger


duty = 0.3
interval = 2
period = 0.02

motor1 = motor.Motor(1)
motor2 = motor.Motor(2)

servo_hor = servo.Servo(1)
servo_vert = servo.Servo(2)
clckh = clock.Clock(servo_hor, period)
clckv = clock.Clock(servo_vert, period)

rcpy.set_state(rcpy.RUNNING)
# enable servos
servo.enable()

# start clock
clckh.start()
clckv.start()


def distanceMeasurement(TRIG,ECHO):
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)
    pulse_start = time.time()
    pulse_end = time.time()
    counter = 0
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
        counter += 1
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)
    return distance


def look_back():
    print("look_back()")
    servo_vert.set(-1.5)
    time.sleep(0.2)


def look_angle(angle=90):
    print("look_angle({})".format(angle))
    time.sleep(0.2)
    if angle > 0 and angle > 90:
        angle = 90
    if angle < 0 and angle < -90:
        angle = -90
    position = angle * 0.015
    servo_hor.set(position)
    servo_vert.set(0)
    time.sleep(0.2)


def say_yes():
    print("say_yes()")
    servo_vert.set(0)
    time.sleep(0.2)
    servo_vert.set(1.5)
    time.sleep(0.2)
    servo_vert.set(-1.5)
    time.sleep(0.2)
    servo_vert.set(1.5)
    time.sleep(0.2)
    servo_vert.set(0)
    time.sleep(0.2)


def say_no():
    print("say_no()")
    servo_vert.set(0)
    time.sleep(0.2)
    servo_hor.set(0)
    time.sleep(0.4)
    servo_hor.set(1.5)
    time.sleep(0.2)
    servo_hor.set(-1.4)
    time.sleep(0.4)
    servo_hor.set(0)
    time.sleep(0.2)


def move_block(blocks):
    d = duty
    if blocks < 0:
        d = d * -1
        blocks = blocks * -1

    motor1.set(d)
    motor2.set(d)

    time.sleep(interval * blocks)

    motor1.set(0)
    motor2.set(0)


def turn_right(angle=90):
    look_angle(angle* -1)
    print("turn_right()".format(angle))
    motor1.set(duty)
    time.sleep(0.0077777 * angle)
    motor1.set(0)


def turn_left(angle=90):
    look_angle(angle)
    print("turn_left({})".format(angle))
    motor2.set(duty)
    time.sleep(0.0077777 * angle)
    motor2.set(0)


def forward(blocks=1):
    print("forward({})".format(blocks))
    if blocks > 0:
        look_angle(0)
    else:
        look_back()
    return move_block(blocks)


def backward(blocks=1):
    print("backward({})".format(blocks))
    return forward(-blocks)


def random_move(force=False):
    rand = random.randint(0, 100)
    if force or rand < 25:
        rand = random.randint(15, 180)
        print("random_move({}) step1".format(str(rand)))
        look_back()
        left = bool(random.getrandbits(1))
        if left:
            turn_left(rand)
        else:
            turn_right(rand)
        backward()
        print("random_move({}) step2".format(str(rand)))
        left = not left
        if left:
            turn_left(rand)
        else:
            turn_right(rand)


def shutdown():
    global running
    running = False


def main():
    global running
    running = True
    print("Init")

    recovered_distance = distanceMeasurement(trigger, echo)
    while running:
        #  TODO: implement stop condition to break the loop and execute the stop commands at the end
        if recovered_distance <= 0 or recovered_distance > 400:
            recovered_distance = 1.111
        while recovered_distance > 80.0:
            print("Distance: [{}] cm. Clear path!".format((str(recovered_distance))))
            say_yes()
            forward()
            time.sleep(1)
            recovered_distance = distanceMeasurement(trigger, echo)
            if recovered_distance <= 0 or recovered_distance > 400:
                recovered_distance = 1.111
            random_move()
        # Found obstacle
        print("Distance: [{}] cm. Dead end!".format(str(recovered_distance)))
        say_no()
        backward(0.5)
        rand = random.randint(0,100)
        print("rand: [{}]".format(str(rand)))
        if rand >= 0 and rand < 40:
            turn_left()
        if rand >= 40 and rand < 80:
            turn_right()
        if rand >= 80:
            random_move(force=True)
        recovered_distance = distanceMeasurement(trigger, echo)

    # stop clock
    clckh.stop()
    clckv.stop()

    # disable servos
    servo.disable()
    print("Done")


if __name__ == '__main__':
    main()
