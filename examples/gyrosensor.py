import ev3dev.ev3 as ev3
import time

if __name__ == "__main__":
    
    gs = ev3.GyroSensor()
    gs.mode='GYRO-ANG'

    while True:
        angle = gs.value()
        print(angle)
        ev3.Sound.tone(1000+angle*10, 1000).wait()
        time.sleep(0.5)
