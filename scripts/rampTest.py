#!/usr/bin/env python3 
import ev3dev.ev3 as ev3
import time

import signal
import sys

SPEED = 200

mLeft = ev3.LargeMotor("outA")
mRight = ev3.LargeMotor("outD")

ts = ev3.TouchSensor("in4")

def signal_handler(sig, frame):
    print('Stopping motors and shutting down')
    mLeft.stop(stop_action="coast")
    mRight.stop(stop_action="coast")
    time.sleep(5)

    sys.exit(0)

if __name__ == "__main__":

    signal.signal(signal.SIGINT, signal_handler)

    while True:

        mLeft.run_forever(speed_sp=SPEED)
        mRight.run_forever(speed_sp=SPEED)

        # print(ts.value())
        
