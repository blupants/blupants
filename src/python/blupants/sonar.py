#!/usr/bin/env python
# -*- coding: utf-8 -*-

from rc_balance_dstr import *
import Adafruit_BBIO.GPIO as GPIO
import time
import random


# TODO: this is only test code for adding a sonar to the eduMIP robot.
# In the future this code should be refactored and merged to the edumip module

# * TRIGGER             P8_12 gpio1[12] GPIO44  out     pulldown                Mode: 7
# * ECHO                P8_11 gpio1[13] GPIO45  in      pulldown                Mode: 7 *** with R 1KOhm (actually 1.2KOhm)
# * GND                 P9_1    GND
# * VCC                 P9_5    VDD_5V

echo = "P8_11"
trigger = "P8_12"
gnd = "P9_1"
vcc = "P9_5"


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
time.sleep(2)


def distanceMeasurement(TRIG,ECHO):
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)
    pulseStart = time.time()
    pulseEnd = time.time()
    counter = 0
    while GPIO.input(ECHO) == 0:
        pulseStart = time.time()
        counter += 1
    while GPIO.input(ECHO) == 1:
        pulseEnd = time.time()

    pulseDuration = pulseEnd - pulseStart
    distance = pulseDuration * 17150
    distance = round(distance, 2)
    return distance

#Configuration
print("trigger: [%s]") % trigger
GPIO.setup(trigger,GPIO.OUT) #Trigger
print("echo: [%s]") % echo
GPIO.setup(echo,GPIO.IN)  #Echo
GPIO.output(trigger, False)
print("Setup completed!")

#Security
GPIO.output(trigger, False)
time.sleep(0.5)

def random_move(force=False):
    rand = random.randint(0, 100)
    if force or rand < 25:
        rand = random.randint(15, 180)
        print("random_move(%s) step1") % str(rand)
        left = bool(random.getrandbits(1))
        if left:
            turn_left(rand)
        else:
            turn_right(rand)
        move_block(-1)
        print("random_move(%s) step2") % str(rand)
        left = not left
        if left:
            turn_left(rand)
        else:
            turn_right(rand)



recoveredDIstance = distanceMeasurement(trigger,echo)
while True:
    if recoveredDIstance <= 0 or recoveredDIstance > 400:
        recoveredDIstance = 1.111
    while recoveredDIstance > 60.0:
        print("Distance: [%s] cm. Clear path!") % str(recoveredDIstance)
        move_block()
        time.sleep(1)
        recoveredDIstance = distanceMeasurement(trigger, echo)
        if recoveredDIstance <= 0 or recoveredDIstance > 400:
            recoveredDIstance = 1.111
        random_move()
    # Found obstacle
    print("Distance: [%s] cm. Dead end!") % str(recoveredDIstance)
    #left = bool(random.getrandbits(1))
    rand = random.randint(0,100)
    print("rand: [%s]") % str(rand)
    if rand >= 0 and rand < 40:
        turn_left()
    if rand >= 40 and rand < 80:
        turn_right()
    if rand >= 80:
        random_move(force=True)
    recoveredDIstance = distanceMeasurement(trigger, echo)


GPIO.cleanup()
print("Done")



