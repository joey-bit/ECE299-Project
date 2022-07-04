from machine import Pin, SPI, I2C # SPI is a class associated with the machine library. 
import utime

# The below specified libraries have to be included. Also, ssd1306.py must be saved on the Pico. 
#from ssd1306 import SSD1306_SPI # this is the driver library and the corresponding class
import framebuf # this is another library for the display. 
from ssd1309 import Display # OLED driver library and the corresponding class Display
from ds3231_port import DS3231 # RTC module driver library and the corresponding class DS3231
#from ds1302 import DS1302
# Define columns and rows of the oled display. These numbers are the standard values. 
#SCREEN_WIDTH = 126 #number of columns #128 for ssd1306, 126 for ssd1309
#SCREEN_HEIGHT = 64 #number of rows

# Initialize I/O pins associated with the oled display SPI interface
spi_sck = Pin(18) # sck stands for serial clock; always be connected to SPI SCK pin of the Pico
spi_sda = Pin(19) # sda stands for serial data;  always be connected to SPI TX pin of the Pico; this is the MOSI
spi_res = Pin(16) # res stands for reset; always be connected to SPI RX pin of the Pico; this is the MISO
spi_dc  = Pin(17) # dc stands for data/commonda; always be connected to SPI CSn pin of the Pico
spi_cs  = Pin(20) # can be connected to any free GPIO pin of the Pico

i2c_scl = Pin(13, Pin.PULL_UP, mode=Pin.OPEN_DRAIN)
i2c_sda = Pin(12, Pin.PULL_UP, mode=Pin.OPEN_DRAIN)

#Input
button = Pin(0, Pin.IN, Pin.PULL_DOWN) # Assigning pin 0 to the button input

#Functional Control Variables 
currentState = 0 # button state initially unpressed

#Constants
pressed = 1
released = 0

#
# SPI Device ID can be 0 or 1. It must match the wiring. 
#
SPI_DEVICE_ID = 0 # Because the display is connected to SPI 0 hardware lines of the Pico
I2C_DEVICE_ID = 0 # Because the RTC is connected to I2C 0 hardware lines of the Pico
I2C_ADDR_RTCM = 104 # Determined by running i2c.scan()

#
# initialize the SPI interface for the OLED display
#
oled_spi = SPI( SPI_DEVICE_ID, baudrate=10000000, sck=spi_sck, mosi=spi_sda )
rtcm_i2c = I2C( I2C_DEVICE_ID, scl=i2c_scl, sda=i2c_sda )

#
# Initialize the display
#
display = Display( oled_spi, cs=spi_cs, dc=spi_dc, rst=spi_res )
ds3231 = DS3231(rtcm_i2c)

"""
print('Initial values')
print('DS3231 time:', ds3231.get_time())
print('RTC time:   ', utime.localtime())
print('Setting DS3231 from RTC')
ds3231.save_time()  # Set DS3231 from RTC
print('DS3231 time:', ds3231.get_time())
print('RTC time:   ', utime.localtime())
ds3231.set_time(2000, 02, 14, 03, 01, 45, 7, 0)
print('DS3231 time:', ds3231.get_time())
print('RTC time:   ', utime.localtime())
"""
#ds3231.set_time(2022, 07, 03, 16, 32, 00, 0, 0)
ds3231.save_time()  # Set DS3231 from RTC

while ( True ):
#
# Clear the buffer
#
        display.clear_buffers()

#
# Update the text on the screen
#
        #rtc = machine.RTC()
        #timestamp = rtc.datetime()
        timestamp = ds3231.get_time()
        datestring="%04d-%02d-%02d" % (timestamp[0:3])
        timestring="%02d:%02d:%02d" % (timestamp[3:6])
        display.draw_text8x8(0, 0, "Testing RTC Module")
        display.draw_text8x8(40, 9, "Line 1")
        display.draw_text8x8(0, 26, "Time: %s" % timestring)
        display.draw_text8x8(0, 35, "Date: %s" % datestring)
        display.draw_text8x8(80, 55, "Line 2")       

#
# Transfer the buffer to the screen
#
        display.present()
"""  
#
# Detect and Debounce Button Press
#
        #Polling for a button press detection
        #If the button is pressed change the state varible accordingly and enter while loop.
        if button.value() == pressed: 
            currentState = pressed
            #While the button is in pressed state poll for a change in the state.
            #If a release is detected, change the state varible accordingly to exit
            #the while loop.
            while currentState == pressed: 
                if button.value() == released:
                    currentState = released
                    Count += 1
"""                   