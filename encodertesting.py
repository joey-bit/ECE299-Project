from machine import Pin
import utime

encoderA = Pin(14, Pin.IN, Pin.PULL_UP)
encoderB = Pin(15, Pin.IN, Pin.PULL_UP)
counter = 0

prev = True
while True:
    if prev != encoderA.value():
        if encoderB.value() != False:
            print("to the left")
        else:
            print("to the right")
    prev = encoderA.value()
    

        
    