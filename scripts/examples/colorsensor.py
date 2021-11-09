import ev3dev.ev3 as ev3
import time

if __name__ == "__main__":
    
    cs = ev3.ColorSensor()
    cs.mode='COL-REFLECT'

    while True:
        print(cs.value())
        time.sleep(0.5)
