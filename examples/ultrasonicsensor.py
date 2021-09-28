import ev3dev.ev3 as ev3
import time

if __name__ == "__main__":
    
    us = ev3.UltrasonicSensor()
    us.mode='US-DIST-CM'

    while True:
        print(us.value())
        time.sleep(0.5)
