#!/usr/bin/env python3 
from re import search
import ev3dev.ev3 as ev3
import time

import signal
import sys

# --------------------- DEVICES ---------------------

# Sensors
cs_left = ev3.ColorSensor("in2")
cs_right = ev3.ColorSensor("in3")
btn = ev3.TouchSensor() # Perhaps port
gyro = gs = ev3.GyroSensor()

# Actuators
mLeft = ev3.LargeMotor("outA")
mRight = ev3.LargeMotor("outD")

# ---------------------- GLOBAL ----------------------
DEBUG = True
PARTY_MODE = True

# States
states = ["lineFollow_Search",
          "lineFollow_Rescue",
          "gripper_released",
          "turnAlign",
          "searchLeft",
          "searchRight"
          ]

# Line follow
# offsetLeft = (66 + 5) / 2.0     # Left sensor offset
# offsetRight = (64 + 5) / 2.0    # Right sensor offset
Kp = 40                         # Proportional gain
Ki = 2                          # Integral gain
Kd = 1                          # Derivative gain
Tp = -700                       # Base speed of robot

# CCFS
TURN_THRESHOLD = 20
TURN_SPEED = -200
ALIGN_WINDOW = 120
DEPLOY_TIME = 200

# -------------------- FUNCTIONS --------------------
def switchState(new_state, debug = 0):
    '''
    State switcher. Takes in new state and checks if state is valid.
    If debug information is enabled, it prints out the new state.
    Returns the new state.
    '''
    
    # Check if state exists
    if new_state not in states:
        print("Invalid new state: '"  + new_state + "'")
        exit()
    
    # Print debug information if enabled
    if (debug):
        print(new_state)
    
    # Return new state
    return new_state

def saturateSpeed(left_speed, right_speed):
    '''
    Function for limiting the commanded speed.
    The EV3 motors throw an exception if the absolute commanded speed is above 999.
    '''
    # Lower cap
    left_speed = max(left_speed, -999)
    right_speed = max(right_speed, -999)
    
    # Upper cap
    left_speed = min(left_speed, 999)
    right_speed = min(right_speed, 999)
    
    return left_speed, right_speed

def signal_handler(sig, frame):
    '''
    Signal handler. Detects program interrupts and stops motors before halting program.
    '''
    
    print('Stopping motors and shutting down')
    mLeft.stop(stop_action="coast")
    mRight.stop(stop_action="coast")
    time.sleep(5)

    sys.exit(0)
    
if __name__ == "__main__":
    
    if PARTY_MODE:
        ev3.Sound.set_volume(100)
        ev3.Sound().speak("Party mode engaged. Step aside virgins.").wait()
        ev3.Sound.play('Undertale  Megalovania.wav')
        
    
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Set sensor modes
    cs_left.mode  = 'COL-REFLECT'
    cs_right.mode = 'COL-REFLECT'
    gs.mode='GYRO-ANG'
    
    # Sensor offsets
    gyro_offset = gs.value()
    offsetLeft = (cs_left.value() + 5) / 2.0
    offsetRight = (cs_right.value() + 5) / 2.0
    
    # Initialize PID parameters
    integral = 0
    lastError = 0
    derivative = 0
    
    # Start state
    state = switchState('lineFollow_Search', DEBUG)
    
    while True:
        
        # PID
        lightValueLeft = cs_left.value()
        lightValueRight = cs_right.value()
        errorLeft = lightValueLeft - offsetLeft
        errorRight = lightValueRight - offsetRight
        error = (errorLeft - errorRight) / 2.0
        
        integral = 0.99 * integral + error
        derivative = error - lastError

        Turn = Kp * error + Ki * integral + Kd * derivative

        left_speed = Tp - Turn
        right_speed = Tp + Turn
        
        left_speed, right_speed = saturateSpeed(left_speed, right_speed)

        
        
        # Crude switch-case implementation in python version < 3.10
        if state == 'lineFollow_Search':
            
            # Stop motors to enable speed setting
            mLeft.stop(stop_action="hold")
            mRight.stop(stop_action="hold")
            
            # Set new speed
            mLeft.run_forever(speed_sp=left_speed)
            mRight.run_forever(speed_sp=right_speed)
            
            if btn.value() == 0:
                # Butten released
                
                # Stop motors to enable speed setting
                mLeft.stop(stop_action="coast")
                mRight.stop(stop_action="coast")
                
                # Switch state
                state = switchState('gripper_released', DEBUG) # Perhaps intermediate state
                
        elif state == 'lineFollow_Rescue':
            
            # Stop motors to enable ned speed setting
            mLeft.stop(stop_action="hold")
            mRight.stop(stop_action="hold")
            
            # Set new speed
            mLeft.run_forever(speed_sp=left_speed)
            mRight.run_forever(speed_sp=right_speed)
        
        elif state == 'gripper_released':
            
            # Wait for gripper to deploy
            mLeft.run_timed(time_sp=DEPLOY_TIME, speed_sp=-400, stop_action='brake')
            mRight.run_timed(time_sp=DEPLOY_TIME, speed_sp=-400, stop_action='brake')
            mLeft.wait_while('running')
            
            # Read gyro in order to zero it
            gyro_offset = gs.value()
            
            # Switch state
            state = switchState('turnAlign', DEBUG)
        
        elif state == 'turnAlign':
            
            # Turn to the left
            mLeft.run_forever(speed_sp=-TURN_SPEED)
            mRight.run_forever(speed_sp=TURN_SPEED)
            
            # Check 
            if abs(gs.value() - gyro_offset) > (180 - ALIGN_WINDOW / 2.0):
                
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
            mLeft.run_forever(speed_sp=-TURN_SPEED)
            mRight.run_forever(speed_sp=TURN_SPEED)
            
            if abs(error) > TURN_THRESHOLD:
                # Line found
                
                # Stop motors
                mLeft.stop(stop_action="hold")
                mRight.stop(stop_action="hold")
                
                # Switch state
                state = switchState('lineFollow_Rescue', DEBUG)
                integral = 0    # Zero integral before switching to linefollow
            
            elif abs(gs.value() - gyro_offset) > (180 - ALIGN_WINDOW / 2.0) + ALIGN_WINDOW:
                # Line not found
                
                # Stop motors
                mLeft.stop(stop_action="hold")
                mRight.stop(stop_action="hold")
                
                # Switch state
                state = switchState('searchRight', DEBUG)
        
        elif state == 'searchRight':
            
            # Turn to the right
            mLeft.run_forever(speed_sp=TURN_SPEED)
            mRight.run_forever(speed_sp=-TURN_SPEED)
            
            if abs(error) > TURN_THRESHOLD:
                # Line found
                
                # Stop motors
                mLeft.stop(stop_action="hold")
                mRight.stop(stop_action="hold")
                
                # Switch state
                state = switchState('lineFollow_Rescue', DEBUG)
                integral = 0    # Zero integral before switching to linefollow
            
            elif abs(gs.value() - gyro_offset) < (180 - ALIGN_WINDOW / 2.0):
                # Line not found
                
                # Stop motors
                mLeft.stop(stop_action="hold")
                mRight.stop(stop_action="hold")
                
                # Switch state
                state = switchState('searchLeft', DEBUG)
                
                
            
        
    
    
    