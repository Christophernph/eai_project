#!/usr/bin/env python3 
from re import search
import ev3dev.ev3 as ev3
import time

import signal
import sys

btn = ev3.TouchSensor() # Perhaps port
    
if __name__ == "__main__":
    
    while True:
        print(btn.value())