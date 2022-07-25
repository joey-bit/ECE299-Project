from machine import Pin

encoderATrigger = False
encoderBTrigger = False
encoderA = Pin(14, Pin.IN, Pin.PULL_UP)
encoderB = Pin(15, Pin.IN, Pin.PULL_UP)
counter = 0
rest_state = True

def encoderAInterrupt(encA):
    global encoderATrigger
    PinFlags = encA.irq().flags()    
    if (( PinFlags & 0x0C ) == 4 ):
        print("EncoderA triggered")
        encoderATrigger = True
        
def encoderBInterrupt(encB):
    global encoderBTrigger
    PinFlags = encB.irq().flags()    
    if (( PinFlags & 0x0C ) == 4 ):
        print("EncoderB triggered")
        encoderBTrigger = True
    
encoderA.irq( handler = encoderAInterrupt, trigger = Pin.IRQ_FALLING, hard = True )
encoderB.irq( handler = encoderBInterrupt, trigger = Pin.IRQ_FALLING, hard = True )


while True:
    if !rest_state:
        if encoderA.value()==1 and encoderB.value()==1:
            encoderATrigger = False
            encoderBTrigger = False
            rest_state = True
    if rest_state:
        if encoderATrigger:
            if encoderBTrigger:
                print("to the left")
                counter+=1
                print(counter)
            else:
                print("to the right")
                counter-=1
                print(counter)
            rest_state = False

    
    

        
    