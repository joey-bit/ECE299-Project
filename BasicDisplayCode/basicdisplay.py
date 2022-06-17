from machine import Pin, SPI # SPI is a class associated with the machine library. 
import utime

# The below specified libraries have to be included. Also, ssd1306.py must be saved on the Pico. 
from ssd1306 import SSD1306_SPI # this is the driver library and the corresponding class
import framebuf # this is another library for the display. 


# Define columns and rows of the oled display. These numbers are the standard values. 
SCREEN_WIDTH = 126 #number of columns #128 for ssd1306, 126 for ssd1309
SCREEN_HEIGHT = 64 #number of rows


# Initialize I/O pins associated with the oled display SPI interface

spi_sck = Pin(18) # sck stands for serial clock; always be connected to SPI SCK pin of the Pico
spi_sda = Pin(19) # sda stands for serial data;  always be connected to SPI TX pin of the Pico; this is the MOSI
spi_res = Pin(16) # res stands for reset; always be connected to SPI RX pin of the Pico; this is the MISO
spi_dc  = Pin(17) # dc stands for data/commonda; always be connected to SPI CSn pin of the Pico
spi_cs  = Pin(20) # can be connected to any free GPIO pin of the Pico

#Functional Control Variable 
button = Pin(0, Pin.IN, Pin.PULL_DOWN) # Assigning pin 0 to the button input
currentState = 0 # initially unpressed

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
oled_spi = SPI( SPI_DEVICE, baudrate= 100000, sck= spi_sck, mosi= spi_sda )

#
# Initialize the display
#
oled = SSD1306_SPI( SCREEN_WIDTH, SCREEN_HEIGHT, oled_spi, spi_dc, spi_res, spi_cs, True )

# Assign a value to a variable
Count = 0

while ( True ):
  
#
# Clear the buffer
#
        oled.fill(0)

#
# Update the text on the screen
#
        oled.text("Welcome to ECE", 6, 0) # Print the text starting from 0th column and 0th row
        oled.text("299", 44, 10) # Print the number starting at 45th column and 10th row
        oled.text("Count is: %4d" % Count, 0, 40 ) # Print the value stored in the variable Count. 
        
#
# Draw box below the text
#
        oled.rect( 0, 58, 126, 6, 1  )        

#
# Transfer the buffer to the screen
#
        oled.show()
   
#
# Detect and Debounce Button Press
#
        if button.value() == pressed:
            currentState = pressed
            while currentState == pressed:
                if button.value() == released:
                    currentState = released
                    Count += 1
                    