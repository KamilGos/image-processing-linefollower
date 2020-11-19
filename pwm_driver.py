import board
import busio
import adafruit_pca9685
from adafruit_servokit import ServoKit
import time

class Engines:
    def __init__(frequency=1500):
        print("Engines initializing...")
        i2c_bus = (busio.I2C(board.SCL_1, board.SDA_1))
        self.pca = adafruit_pca9685.PCA9685(i2c_bus=i2c_bus0, address=0x41)
        self.pca.frequency = frequency
        self.eRB = self.pca.channels[0] # engine right backward speed
        self.eRF = self.pca.channels[1] # engine right forward speed
        self.eLB = self.pca.channels[3] # engine left backward speed
        self.eLF = self.pca.channels[2] # engine left forward speed
        self.eRB.duty_cycle = 0
        self.eRF.duty_cycle = 0
        self.eLB.duty_cycle = 0
        self.eLF.duty_cycle = 0
        print("Engines ready")

    def changeFrequency(new_freq):
        if new_freq>=1 && new_freq<=1600:
            try:
                self.pca.frequency = int(new_freq) 
            except:
                print("Set frequency error")
        else:
            raise Exception("Frequency should be in [1; 1600] range")
    
    def bothForward(speed)
        self.eLB.duty_cycle = 0
        self.eLF.duty_cycle = speed
        self.eRB.duty_cycle = 0
        self.eRF.duty_cycle = speed

    def bothBackward(speed)
        self.eLB.duty_cycle = speed
        self.eLF.duty_cycle = 0
        self.eRB.duty_cycle = speed
        self.eRF.duty_cycle = 0

    def bothStop()
        self.eLB.duty_cycle = 0
        self.eLF.duty_cycle = 0
        self.eRB.duty_cycle = 0
        self.eRF.duty_cycle = 0


class Tilt:
    def __init__():
        print("Tilt initializing...")
        i2c_bus = (busio.I2C(board.SCL_1, board.SDA_1))
        self.kit = ServoKit(channels=16, i2c=i2c_bus0, address=0x40)
        self.servo = self.kit.servo[0]
        print("Tilt ready")

    # input: [-15; 15]
    def setTilt(tilt)
        if -15<=tilt<=15:
            try:
                self.servo.angle = 90+tilt
            except:
                print("Servo set angle error")
        else:
            raise Exception("Tilt should be in [-15; 15] range")



