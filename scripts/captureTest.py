#!/usr/bin/env python3 
from re import search
import ev3dev.ev3 as ev3
import time

import signal
import sys

# ---------- Functions ----------
def switchState(new_state, debug = 0):
    
    if (debug):
        print(new_state)
    
    return new_state

# ---------- Devices ----------

# Sensors
cs_left = ev3.ColorSensor("in2")
cs_right = ev3.ColorSensor("in3")
btn = ev3.TouchSensor() # Perhaps port
gyro = gs = ev3.GyroSensor()

# Actuators
mLeft = ev3.LargeMotor("outA")
mRight = ev3.LargeMotor("outD")

# ---------- Global ----------
offsetLeft = (66 + 5) / 2.0     # Perhaps read in at start
offsetRight = (64 + 5) / 2.0   # Perhaps read in at start

DEBUG = True
TURN_THRESHOLD = 20

def signal_handler(sig, frame):
    print('Stopping motors and shutting down')
    mLeft.stop(stop_action="coast")
    mRight.stop(stop_action="coast")
    time.sleep(5)

    sys.exit(0)
    
if __name__ == "__main__":
    
    signal.signal(signal.SIGINT, signal_handler)
    
    '''
    For now, no PID control loop, but this will be there in the future
    '''
    
    # Set sensor modes
    cs_left.mode  = 'COL-REFLECT'
    cs_right.mode = 'COL-REFLECT'
    gs.mode='GYRO-ANG'
    
    # Sensor offsets
    gyro_offset = gs.value()
    
    # Start state
    state = switchState('lineFollow_Search', DEBUG)
    
    while True:
        
        # PID
        # Get PID error
        lightValueLeft = cs_left.value()
        lightValueRight = cs_right.value()
        errorLeft = lightValueLeft - offsetLeft
        errorRight = lightValueRight - offsetRight
        error = (errorLeft - errorRight) / 2.0
        # print(error, lightValueLeft, lightValueRight)
        
        # Crude switch-case implementation in python version < 3.10
        if state == 'lineFollow_Search':
            # Harcode drive with certain velocity
            mLeft.run_forever(speed_sp=200)
            mRight.run_forever(speed_sp=200)
            
            if btn.value() == 0:
                # Butten released
                state = switchState('gripper_released', DEBUG) # Perhaps intermediate state
        elif state == 'lineFollow_Rescue':
            # Harcode drive with certain velocity
            mLeft.run_forever(speed_sp=200)
            mRight.run_forever(speed_sp=200)
        
        elif state == 'gripper_released':
            
             # Wait for gripper to deploy
            time.sleep(0.5)
            
            # Stop motors
            mLeft.stop(stop_action="coast")
            mRight.stop(stop_action="coast")
            
            # Read gyro in order to zero it
            gyro_offset = gs.value()
            
            # Switch state
            state = switchState('turnAlign', DEBUG)
        
        elif state == 'turnAlign':
            
            # Turn to the left
            mLeft.run_forever(speed_sp=-200)
            mRight.run_forever(speed_sp=200)
            
            # Check 
            if abs(gs.value() - gyro_offset) > 120:
                
                # Stop motors
                mLeft.stop(stop_action="hold")
                mRight.stop(stop_action="hold")
                
                # Switch state
                state = switchState('searchLeft', DEBUG)
        
        elif state == 'searchLeft':
            
            # Get PID error
            lightValueLeft = cs_left.value()
            lightValueRight = cs_right.value()
            errorLeft = lightValueLeft - offsetLeft
            errorRight = lightValueRight - offsetRight
            error = (errorLeft - errorRight) / 2.0
            
            # Turn to the left
            mLeft.run_forever(speed_sp=-200)
            mRight.run_forever(speed_sp=200)
            
            if abs(error) > TURN_THRESHOLD:
                # Line found
                
                # Stop motors
                mLeft.stop(stop_action="hold")
                mRight.stop(stop_action="hold")
                
                # Switch state
                state = switchState('lineFollow_Rescue', DEBUG)
            
            elif abs(gs.value() - gyro_offset) > 240:
                # Line not found
                
                # Stop motors
                mLeft.stop(stop_action="hold")
                mRight.stop(stop_action="hold")
                
                # Switch state
                state = switchState('searchRight', DEBUG)
        
        elif state == 'searchRight':
            
            # Turn to the left
            mLeft.run_forever(speed_sp=200)
            mRight.run_forever(speed_sp=-200)
            
            if abs(error) > TURN_THRESHOLD:
                # Line found
                
                # Stop motors
                mLeft.stop(stop_action="hold")
                mRight.stop(stop_action="hold")
                
                # Switch state
                state = switchState('lineFollow_Rescue', DEBUG)
            
            elif abs(gs.value() - gyro_offset) < 120:
                # Line not found
                
                # Stop motors
                mLeft.stop(stop_action="hold")
                mRight.stop(stop_action="hold")
                
                # Switch state
                state = switchState('searchLeft', DEBUG)
                
                
            
        
    
    
    