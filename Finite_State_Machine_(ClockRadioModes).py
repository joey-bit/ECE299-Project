#Finite State Machine Code for Clock Radio Modes
from machine import Pin, SPI, Timer # SPI is a class associated with the machine library. 
import utime

# The below specified libraries have to be included. Also, ssd1309.py must be saved on the Pico. 
from ssd1309 import Display # this is the driver library and the corresponding class
from xglcd_font import XglcdFont #Fonts
import framebuf # this is another library for the display. 

# Initialize I/O pins associated with the oled display SPI interface
spi_res = Pin(16) # res stands for reset; always be connected to SPI RX pin of the Pico; this is the MISO
spi_dc  = Pin(17) # dc stands for data/commonda; always be connected to SPI CSn pin of the Pico
spi_sck = Pin(18) # sck stands for serial clock; always be connected to SPI SCK pin of the Pico
spi_sda = Pin(19) # sda stands for serial data;  always be connected to SPI TX pin of the Pico; this is the MOSI
spi_cs  = Pin(20) # can be connected to any free GPIO pin of the Pico

# Initialize I/O pins associated with button inputs
button_snooze = Pin(0, Pin.IN, Pin.PULL_DOWN)
button_mode = Pin(1, Pin.IN, Pin.PULL_DOWN)
button_up = Pin(2, Pin.IN, Pin.PULL_DOWN)
button_down = Pin(3, Pin.IN, Pin.PULL_DOWN)

#State Variable
currentState_of_button_snooze = 0 # initially unpressed
currentState_of_button_mode = 0 # initially unpressed
currentState_of_button_up = 0 # initially unpressed
currentState_of_button_down = 0 # initially unpressed

#Constants
pressed = 1
released = 0

#
# SPI Device ID can be 0 or 1. It must match the wiring. 
#
SPI_DEVICE = 0 # Because the peripheral is connected to SPI 0 hardware lines of the Pico

#
# initialize the SPI interface for the OLED display
#
spi = SPI( SPI_DEVICE, baudrate=10000000, sck=spi_sck, mosi=spi_sda )

#
# Initialize the display object
#
display = Display( spi, cs=spi_cs, dc=spi_dc, rst=spi_res )

#
#Fonts
#
bally = XglcdFont('fonts/Bally7x9.c', 7, 9)
rototron = XglcdFont('fonts/Robotron13x21.c', 13, 21)
unispace = XglcdFont('fonts/Unispace12x24.c', 12, 24)
wendy = XglcdFont('fonts/Wendy7x8.c', 7, 8)

#
#Time Variable
#
clock_time = "12:34"#str(utime.localtime())#
alarm_time = 0#"08:00"

def toggleTimeFormat(time_val):
    pass

##=============================================================
##TRANSITIONS

class Transitions(object):
    def __init__(self, toState):
        self.toState = toState
        
    def Execute(self):
        print("Transitioning...")
        
##=============================================================
##STATES
        
class State(object):
    def __init__(self,FSM):
        

while ( True ):

#
# Clear the buffer
#
    display.clear_buffers()
    
#
# Update the text on the screen
#
    #display.draw_text8x8(42, 0, "CLOCK")
    display.draw_text( 42, 0, "CLOCK", bally )
    display.draw_text( 34, 22, clock_time, rototron )
    #display.draw_text8x8( 0, 0, clock_time[0:11] )
    #display.draw_text8x8( 0, 12, clock_time[12:] )
    #display.draw_text8x8( 6, 52, "ALARM: " + str(alarm_time) )
    display.draw_text( 6, 52, "ALARM: " + str(alarm_time), bally )

#
# Transfer the buffer to the screen
#
    display.present()
    
#
# Update displayed number
#
    if button_up.value() == pressed:
        currentState_of_button_up = pressed
        while currentState_of_button_up == pressed:
            if button_up.value() == released:
                currentState_of_button_up = released
                alarm_time += 1
                print("UP")
                    
    if button_down.value() == pressed:
        currentState_of_button_down = pressed
        while currentState_of_button_down == pressed:
            if button_down.value() == released:
                currentState_of_button_down = released
                alarm_time -= 1
                print("DOWN")
                
    if button_mode.value() == pressed:
        currentState_of_button_mode = pressed
        while currentState_of_button_mode == pressed:
            if button_mode.value() == released:
                currentState_of_button_mode = released
                #alarm_time -= 1
                print("MODE")
                display.clear_buffers()
                    
    if button_snooze.value() == pressed:
        currentState_of_button_snooze = pressed
        while currentState_of_button_snooze == pressed:
            if button_snooze.value() == released:
                currentState_of_button_snooze = released
                #alarm_time += 1
                print("SNOOZE")
