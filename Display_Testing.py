#This code will be used to test the OLED display
from machine import Pin, SPI, Timer # SPI is a class associated with the machine library. 
import utime

#import datetime

# The below specified libraries have to be included. Also, ssd1309.py must be saved on the Pico. 
from ssd1309 import Display # this is the driver library and the corresponding class
from xglcd_font import XglcdFont #Fonts
import framebuf # this is another library for the display.
from fm_radio import Radio

# Define columns and rows of the oled display. These numbers are the standard values.
#Already defined in the ssd1309 library
#SCREEN_WIDTH = 126 #number of columns #128 for ssd1306, 126 for ssd1309
#SCREEN_HEIGHT = 64 #number of rows

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
toggled_snooze = 0 # variable defining whether a button was toggled
toggled_mode = 0
toggled_up = 0
toggled_down = 0
currentState_of_button = 0
mode_global = "clock" # default display state is clock
current_frequency = 100.3
fm_radio = Radio( 100.3, 2, False ) #Initialize radio

#
#Time Variable
#

clock_time_12 = 0
time_format = 24
alarm_time = 0#"08:00"
#timer init

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

def switch_mode_global():
    global mode_global
    if mode_global == "clock":
        mode_global = "alarm"
        print("Current mode is alarm")
    elif mode_global == "alarm":
        mode_global = "radio"
        print("Current mode is radio")
    elif mode_global == "radio":
        mode_global = "clock"
        print("Current mode is clock")
    elif mode_global == "snooze":
        mode_global = "clock"
        print("Current mode is clock")
            
def button_toggle_detect(button_id):
    global currentState_of_button, toggled_snooze, toggled_up, toggled_down, toggled_mode
    if button_id.value() == pressed:
        currentState_of_button = pressed
        while currentState_of_button == pressed:
            if button_id.value() == released:
                currentState_of_button = released
                if button_id == button_snooze:
                    toggled_snooze = 1
                if button_id == button_mode:
                    toggled_mode = 1
                if button_id == button_up:
                    toggled_up = 1
                if button_id == button_down:
                    toggled_down = 1
def set_12_format():
    global time_hr, time_min, clock_time_12
    time_hr_12 = time_hr
    if time_hr_12 > 12:
        am_pm = "PM"
        time_hr_12 -=12
    elif time_hr_12 == 12:
        am_pm = "PM"
    elif time_hr_12 == 0:
        time_hr_12 = 12
        am_pm = "AM"
    else:
        am_pm = "AM"
        
    clock_time_12 = ('{:02d}'.format(time_hr_12) + ":" + '{:02d}'.format(time_min) + am_pm)
    
def set_time():
    global clock_time, time_hr, time_min, toggled_up, toggled_down, toggled_mode
    cursor = "hour"
    display.clear_buffers()
    display.draw_text( 42, 0, "SET TIME", bally )
    display.draw_text( 34, 22, clock_time, rototron )
    display.present()
    utime.sleep_ms(1000)
    while (cursor != "exit"):
        button_toggle_detect(button_up)
        button_toggle_detect(button_down)
        button_toggle_detect(button_mode)
        if cursor == "hour":
            if toggled_up:
                time_hr += 1
                toggled_up = 0
            if toggled_down:
                time_hr -= 1
                toggled_down = 0
            if time_hr > 23:
                time_hr = 0
            if time_hr < 0:
                time_hr = 23
            if toggled_mode:
                cursor = "min"
                toggled_mode = 0
            display.clear_buffers()
            clock_time = ('{:02d}'.format(time_hr) + ":" + '{:02d}'.format(time_min))
            display.draw_text( 42, 0, "SET HOUR", bally )
            display.draw_text( 34, 22, clock_time, rototron )
            display.present()
        if cursor == "min":
            if toggled_up:
                time_min += 1
                toggled_up = 0
            if toggled_down:
                time_min -= 1
                toggled_down = 0
            if time_min > 59:
                time_hr = 0
            if time_hr < 0:
                time_hr = 59
            if toggled_mode:
                cursor = "exit"
                toggled_mode = 0
            display.clear_buffers()
            clock_time = ('{:02d}'.format(time_hr) + ":" + '{:02d}'.format(time_min))
            display.draw_text( 42, 0, "SET MIN", bally )
            display.draw_text( 34, 22, clock_time, rototron )
            display.present()   
             
def run_radio_menu():
    global current_frequency, radio_configured, fm_radio
    exit_status = 0
    while (exit_status == 0):          
    #
    # display the menu
    #  
        print("")
        print( "ECE 299 FM Radio Demo Menu" );
        print("")
        print( "1 - change radio frequency" )
        print( "2 - change volume level" )
        print( "3 - mute audio" )
        print( "4 - read current settings" )
        print( "5 - exit configuration menu")
        
        select = input( "Enter menu number > " )
    #
    # Set radio frequency
    #
        if ( select == "1" ):
            Frequency = input( "Enter frequncy in Mhz ( IE 100.3 ) > " )

            if ( fm_radio.SetFrequency( Frequency ) == True ):
                fm_radio.ProgramRadio()
            else:
                print( "Invalid frequency( Range is 88.0 to 108.0 )" )
    #
    # Set volume level of radio
    #
        elif ( select == "2" ):
            Volume = input( "Enter volume level ( 0 to 15, 15 is loud ) > " )
            
            if ( fm_radio.SetVolume( Volume ) == True ):
                fm_radio.ProgramRadio()
            else:
                print( "Invalid volume level( Range is 0 to 15 )" )        
    #        
    # Enable mute of radio       
    #        
        elif( select == "3" ):
            Mute = input( "Enter mute ( 1 for Mute, 0 for audio ) > " )
            
            if ( fm_radio.SetMute( Mute ) == True ):
                fm_radio.ProgramRadio()
            else:
                print( "Invalid mute setting" )
    #
    # Display radio current settings
    #
        elif( select == "4" ):
            Settings = fm_radio.GetSettings()

            print( Settings )
            print("")
            print("Radio Status")
            print("")

            print( "Mute: ", end="" )
            if ( Settings[0] == True ):
                print( "enabled" )
            else:
                print( "disabled" )

            print( "Volume: %d" % Settings[1] )

            print( "Frequency: %5.1f" % Settings[2] )

            print( "Mode: ", end="" )
            if ( Settings[3] == True ):
                print( "stereo" )
            else:
                print( "mono" )
        elif( select == "5" ):
            exit_status = 1
        else:
            print( "Invalid menu option" )
        
    Settings = fm_radio.GetSettings()
    current_frequency = Settings[2]
    
while ( True ):
    #update time
    localtime = utime.localtime()
    time_hr = localtime[3]
    time_min = localtime[4]
    time_sec = localtime[5]
    clock_time = ('{:02d}'.format(time_hr) + ":" + '{:02d}'.format(time_min))
#
# Clear the buffer
#
    display.clear_buffers()
#
# Update the text on the screen
#
    if mode_global == "clock":
        #display.draw_text8x8(42, 0, "CLOCK")
        if time_format == 24:
            display.draw_text( 42, 0, "CLOCK", bally )
            display.draw_text( 34, 22, clock_time, rototron )
        if time_format == 12:
            set_12_format()
            display.draw_text( 42, 0, "CLOCK", bally )
            display.draw_text( 20, 22, clock_time_12, rototron )
            
        if (toggled_up):
            time_format = 24
            print("24hr format")
            toggled_up = 0
        if (toggled_down):
            time_format = 12
            print("12hr format")
            toggled_down = 0
            
        if (toggled_snooze):
            set_time()
            toggled_snooze = 0
        #display.draw_text8x8( 0, 0, clock_time[0:11] )
        #display.draw_text8x8( 0, 12, clock_time[12:] )
        #display.draw_text8x8( 6, 52, "ALARM: " + str(alarm_time) )
    if mode_global == "alarm":
        display.draw_text( 42, 0, "ALARM: " + str(alarm_time), bally )
        display.draw_text( 34, 22, "00:00", rototron )
    if mode_global == "radio":
        if (toggled_snooze):
            display.clear_buffers()
            display.draw_text( 42, 0, "RADIO", bally )
            display.draw_text( 26, 22, "CONFIG", rototron )
            display.present()
            run_radio_menu()
            display.clear_buffers()
            toggled_snooze = 0
        if (toggled_up):
            volume_up()
            toggled_up = 0
        if (toggled_down):
            volume_down()
            toggled_down = 0
        display.draw_text( 42, 0, "RADIO", bally )
        display.draw_text( 22, 22, "%5.1f" % current_frequency + "FM", rototron )
    if mode_global == "snooze":
        display.clear_buffers()
        display.draw_text( 26, 22, "SNOOZE", rototron )

#
# Transfer the buffer to the screen
#
    display.present()
    
#
# Update displayed number
#
    button_toggle_detect(button_snooze)
    button_toggle_detect(button_mode)
    button_toggle_detect(button_down)
    button_toggle_detect(button_up)
    
    if toggled_mode == 1:
        print("MODE")
        switch_mode_global()
        toggled_mode = 0
        
    if encoder_touched:
        chnage_volume()

                
                