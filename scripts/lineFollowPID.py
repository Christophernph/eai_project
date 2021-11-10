#!/usr/bin/env python3 
import ev3dev.ev3 as ev3
import time

import signal
import sys

MAX_SPEED = 999

# PID variables
Kp = 40
Ki = 2
Kd = 1

offsetLeft = (80 + 7) / 2.0
offsetRight = (89 + 8) / 2.0
Tp = -950

integral = 0
lastError = 0
derivative = 0

# Devices
cs_left = ev3.ColorSensor("in2")
cs_right = ev3.ColorSensor("in3")
mLeft = ev3.LargeMotor("outA")
mRight = ev3.LargeMotor("outD")

def signal_handler(sig, frame):
    print('Stopping motors and shutting down')
    mLeft.stop(stop_action="coast")
    mRight.stop(stop_action="coast")
    time.sleep(5)

    sys.exit(0)

if __name__ == "__main__":

    signal.signal(signal.SIGINT, signal_handler)
    #signal.pause()
    
    cs_left.mode  = 'COL-REFLECT'
    cs_right.mode = 'COL-REFLECT'

    #ev3.Sound().speak("It's time to kick gum and chew ass... And I'm all out of ass")
    # ev3.Sound().beep()
    # ev3.Sound.play('Undertale  Megalovania.wav')
    # ev3.Sound.set_volume(100)

    while True:

        lightValueLeft = cs_left.value() # State
        lightValueRight = cs_right.value() # State
        errorLeft = lightValueLeft - offsetLeft
        errorRight = lightValueRight - offsetRight

        error = (errorLeft - errorRight) / 2.0

        integral = 0.99 * integral + error
        derivative = error - lastError

        Turn = Kp * error + Ki * integral + Kd * derivative

        left_speed = Tp - Turn
        right_speed = Tp + Turn

        # Saturate speed
        if left_speed > MAX_SPEED:
            left_speed = MAX_SPEED
        if left_speed < -MAX_SPEED:
            left_speed = -MAX_SPEED
        if right_speed > MAX_SPEED:
            right_speed = MAX_SPEED
        if right_speed < -MAX_SPEED:
            right_speed = -MAX_SPEED

        mLeft.stop(stop_action="hold")
        mRight.stop(stop_action="hold")
        # print(lightValueLeft, lightValueRight)
        
        
        mLeft.run_forever(speed_sp=left_speed)
        mRight.run_forever(speed_sp=right_speed)
        
        # print(errorLeft, errorRight, error)
        # print(left_speed, right_speed)
        
