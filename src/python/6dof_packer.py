import random
global arm_ready_pos, arm_rest_pos


def random_behavior():
    global robot
    max_range = 10
    cur_angles = robot.get_servos_pos()[:]
    rand_main = random.randint(0, max_range)
    #robot.say("rand_main={rand_main}".format(rand_main=rand_main))
    if rand_main == max_range:
        rand1 = random.randint(0, max_range)
        #robot.say("rand1={rand1}".format(rand1=rand1))
        if rand1 == 0:
            robot.set_servo(7, 90)
            robot.set_servo(7, -90)
            robot.set_servo(7, cur_angles[6])
        if rand1 == 1:
            robot.claw_toggle()
            robot.set_servo(7, 90)
            robot.set_servo(7, cur_angles[6])
            robot.claw_toggle()
        if rand1 == 2:
            robot.turn_left(45)
            robot.claw_toggle()
            robot.set_servo(7, 90)
            robot.set_servo(7, cur_angles[6])
            robot.claw_toggle()
            robot.turn_left(0)
        if rand1 == 3:
            robot.turn_left(90)
            robot.set_servo(7, 90)
            robot.set_servo(7, -90)
            robot.set_servo(7, cur_angles[6])
            robot.turn_left(0)
        if rand1 == 4:
            robot.turn_right(45)
            robot.set_servo(7, 60)
            robot.set_servo(7, cur_angles[6])
            robot.turn_left(0)
        if rand1 == 5:
            robot.turn_right(80)
            robot.sleep(2)
            robot.turn_left(30)
            robot.sleep(1)
            robot.turn_left(0)
        if rand1 == 6:
            robot.turn_left(45)
            robot.set_servo(7, 90)
            robot.set_servo(7, -90)
            robot.set_servo(7, cur_angles[6])
            robot.turn_right(45)
            robot.turn_left(30)
            robot.sleep(1)
            robot.turn_left(0)
        if rand1 == 7:
            robot.set_servo(6, 60)
            robot.set_servo(6, cur_angles[5])
        if rand1 == 8:
            robot.set_servo(6, 60)
            robot.claw_toggle()
            robot.set_servo(7, 60)
            robot.set_servo(7, cur_angles[6])
            robot.claw_toggle()
            robot.set_servo(6, cur_angles[5])
        if rand1 == 9:
            robot.turn_left(45)
            robot.set_servo(6, 60)
            robot.claw_toggle()
            robot.set_servo(7, 60)
            robot.set_servo(7, cur_angles[6])
            robot.claw_toggle()
            robot.set_servo(6, cur_angles[5])
            robot.turn_left(0)
        if rand1 == 10:
            robot.turn_right(30)
            robot.set_servo(6, 70)
            robot.claw_toggle()
            robot.set_servo(7, 60)
            robot.set_servo(7, cur_angles[6])
            robot.claw_toggle()
            robot.set_servo(6, cur_angles[5])
            robot.turn_left(0)

def put_in_the_bag():
    global robot
    global arm_ready_pos, arm_rest_pos

    robot.say("Grabbing item...")
    robot.set_servo(7, 90)
    robot.set_servo(7, 0)
    robot.move_arm(arm_rest_pos)
    cur_angles = robot.get_servos_pos()
    servo6_pos = cur_angles[5]
    servo5_pos = cur_angles[4]
    servo4_pos = cur_angles[3]
    robot.claw_close()
    robot.set_servo(6, servo6_pos - 10)
    robot.set_servo(5, servo5_pos + 10)
    robot.set_servo(4, servo4_pos - 10)
    robot.turn_left()
    robot.sleep(0.5)
    robot.say("Dropping item into the bag...")
    robot.claw_open()
    robot.sleep(0.1)
    robot.turn_left(0)
    # robot.set_servo(6, servo6_pos)
    # robot.set_servo(5, servo5_pos)
    # robot.set_servo(4, servo4_pos)
    robot.move_arm(arm_ready_pos)
    robot.say("Bag is ready to pick-up!")

d = -1
prev_distance = d

arm_ready_pos = robot.get_servos_pos("arm_ready_pos", fmt="json")
arm_rest_pos = robot.get_servos_pos("arm_rest_pos", fmt="json")
robot.move_arm(arm_ready_pos)
robot.sleep(3)
robot.say_yes()

running = True
while running:
    prev_distance = d
    d = robot.read_distance()
    if d <= 0:
        d = 100
    robot.sleep(2)
    if 10 < d < 20 and 10 < prev_distance < 20:
        put_in_the_bag()
        robot.say("Found item within range!")
    else:
        #robot.say("Nothing to do. d={d}".format(d=d))
        random_behavior()

    if d < 5 and prev_distance < 5:
        running = False
        robot.say("Too close, good bye!")
