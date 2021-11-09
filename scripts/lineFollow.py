import ev3dev.ev3 as ev3
import time

import signal
import sys

THRESH = 25
DEFAULT_SPEED = 150
TURN_SPEED = -250

# Devices
cs_left = ev3.ColorSensor("in1")
cs_right = ev3.ColorSensor("in4")
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
    
    cs_left.mode='COL-REFLECT'
    cs_right.mode='COL-REFLECT'

    #ev3.Sound().speak("It's time to kick gum and chew ass... And I'm all out of ass")
    ev3.Sound().beep()

    while True:

        # Default travel speed
        left_speed = DEFAULT_SPEED;
        right_speed = DEFAULT_SPEED;

        if (cs_left.value() < THRESH):
            # Line seen on left side, reduce left speed
            left_speed = TURN_SPEED
            mLeft.stop(stop_action="hold")

        if (cs_right.value() < THRESH):
            # Line seen on right side, reduce right speed
            right_speed = TURN_SPEED
            mRight.stop(stop_action="hold")

        if (cs_left.value() < THRESH) and (cs_right.value() < THRESH):
            # If both see line, drive forwards
            left_speed = DEFAULT_SPEED
            right_speed = DEFAULT_SPEED

        # Set motor speeds
        mLeft.run_forever(speed_sp=left_speed)
        mRight.run_forever(speed_sp=right_speed)

        print(str(cs_left.value()) + " " + str(cs_right.value()))
        
