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
fm_radio = Radio( 101.9, 2, False ) #Initialize radio
mute = False
current_frequency = 101.9
current_volume = 2

#
#Time Variable
#

clock_time_12 = 0
alarm_time_12 = 0
time_format = 24
alarm_hr = 0
alarm_min = 0
alarm_sec = 0
alarm_time = ('{:02d}'.format(alarm_hr) + ":" + '{:02d}'.format(alarm_min))
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
    elif mode_global == "volume":
        mode_global = "radio"
        print("Current mode is radio")
            
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
                    
def set_12_format(hr_obj, which):
    global time_hr, time_min, alarm_hr, alarm_min, clock_time_12, alarm_time_12
    time_hr_12 = hr_obj
    if time_hr_12 > 12:
        am_pm = " PM"
        time_hr_12 -=12
    elif time_hr_12 == 12:
        am_pm = " PM"
    elif time_hr_12 == 0:
        time_hr_12 = 12
        am_pm = " AM"
    else:
        am_pm = " AM"
    if which == "clock": 
        clock_time_12 = str(('{:02d}'.format(time_hr_12) + ":" + '{:02d}'.format(time_min) + am_pm))
    if which == "alarm":
        alarm_time_12 = str(('{:02d}'.format(time_hr_12) + ":" + '{:02d}'.format(alarm_min) + am_pm))
    
def set_time_universal(time_string_obj, hr_obj, min_obj, top_text):
    global toggled_up, toggled_down, toggled_mode, clock_time, alarm_time, time_hr, time_min, alarm_hr, alarm_min
    cursor = "hour"
    display.clear_buffers()
    if top_text == "SET TIME":
        display.draw_text( 16, 22, top_text, rototron )
    if top_text == "SET ALARM":
        display.draw_text( 2, 22, top_text, rototron )
    display.present()
    utime.sleep_ms(1500)
    while (cursor != "exit"):
        button_toggle_detect(button_up)
        button_toggle_detect(button_down)
        button_toggle_detect(button_mode)
        if cursor == "hour":
            if toggled_up:
                hr_obj += 1
                toggled_up = 0
            if toggled_down:
                hr_obj -= 1
                toggled_down = 0
            if hr_obj > 23:
                hr_obj = 0
            if hr_obj < 0:
                hr_obj = 23
            if toggled_mode:
                cursor = "min"
                toggled_mode = 0
            display.clear_buffers()
            time_string_obj = ('{:02d}'.format(hr_obj) + ":" + '{:02d}'.format(min_obj))
            display.draw_text( 36, 0, "SET HOUR", bally )
            display.draw_text( 34, 22, time_string_obj, rototron )
            display.present()
        if cursor == "min":
            if toggled_up:
                min_obj += 1
                toggled_up = 0
            if toggled_down:
                min_obj -= 1
                toggled_down = 0
            if min_obj > 59:
                min_obj = 0
            if min_obj < 0:
                min_obj = 59
            if toggled_mode:
                cursor = "exit"
                toggled_mode = 0
            display.clear_buffers()
            time_str_obj = ('{:02d}'.format(hr_obj) + ":" + '{:02d}'.format(min_obj))
            display.draw_text( 36, 0, "SET MIN", bally )
            display.draw_text( 34, 22, time_str_obj, rototron )
            display.present()
    if top_text == "SET TIME":
        clock_time = time_str_obj
        time_hr = hr_obj
        time_min = min_obj
    if top_text == "SET ALARM":
        alarm_time = time_str_obj
        alarm_hr = hr_obj
        alarm_min = min_obj
        
def volume_change(up_down):
    global fm_radio, current_volume
    
    if (up_down == "up"):      
        if ( fm_radio.SetVolume( current_volume + 1)):
                fm_radio.ProgramRadio()
                current_volume += 1
            
    if (up_down == "down"):      
        if ( fm_radio.SetVolume( current_volume - 1)):
                fm_radio.ProgramRadio()
                current_volume -= 1
                       
def run_radio_menu():
    global current_frequency, radio_configured, fm_radio, display
    exit_status = 0
    display.clear_buffers()
    while (exit_status == 0):
        display.draw_text( 26, 22, "CONFIG", rototron )
        display.present()
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
                current_frequency = float(Frequency)
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
        
   
    
#initial time set

timeset = False
#Main Loop    
while ( True ):
    localtime = utime.localtime()
    time_sec = localtime[5]
    if not timeset:
        time_hr = localtime[3]
        time_min = localtime[4]      
        clock_time = ('{:02d}'.format(time_hr) + ":" + '{:02d}'.format(time_min) + ":" '{:02d}'.format(time_sec))
    
    # Clear the buffer
    display.clear_buffers()

    # Cycle through system states
    if mode_global == "clock":
        #Check fore time format
        if time_format == 24:
            display.draw_text( 46, 0, "CLOCK", bally )
            display.draw_text( 20, 22, clock_time, rototron )
        if time_format == 12:
            set_12_format(time_hr, "clock")
            display.draw_text( 46, 0, "CLOCK", bally )
            display.draw_text( 16, 22, clock_time_12, rototron )
        #Switch time formats    
        if (toggled_up):
            time_format = 24
            print("clock - 24hr format")
            toggled_up = 0
        if (toggled_down):
            time_format = 12
            print("clock - 12hr format")
            toggled_down = 0
        #Enter set time function    
        if (toggled_snooze):
            set_time_universal(clock_time, time_hr, time_min, "SET TIME")
            timeset = True
            toggled_snooze = 0
        clock_time = ('{:02d}'.format(time_hr) + ":" + '{:02d}'.format(time_min) + ":" '{:02d}'.format(time_sec))
        
    if mode_global == "alarm":        
        #Check fore time format
        if time_format == 24:
            display.draw_text( 46, 0, "ALARM", bally )
            display.draw_text( 34, 22, alarm_time, rototron )
        if time_format == 12:
            set_12_format(alarm_hr, "alarm")
            display.draw_text( 46, 0, "ALARM", bally )
            display.draw_text( 16, 22, alarm_time_12, rototron )
        #Switch time formats    
        if (toggled_up):
            time_format = 24
            print("alarm - 24hr format")
            toggled_up = 0
        if (toggled_down):
            time_format = 12
            print("alarm - 12hr format")
            toggled_down = 0
        if (toggled_snooze):
            set_time_universal(alarm_time, alarm_hr, alarm_min, "SET ALARM")
            toggled_snooze = 0
        
    if mode_global == "radio":
        
        if (toggled_snooze):
            mute = not mute
            if mute:
                display.draw_text( 46, 0, "RADIO", bally )
                display.draw_bitmap("mute_perfect.mono", 46, 22, 24, 24, True, 0)
                display.present()
                utime.sleep_ms(750)
            if not mute:
                display.draw_text( 46, 0, "RADIO", bally )
                display.draw_bitmap("unmute_perfect.mono", 46, 22, 24, 24, True, 0)
                display.present()
                utime.sleep_ms(750)
            toggled_snooze = 0
            
        if (toggled_up):
            mode_global = "volume"
            
        if (toggled_down):
            mode_global = "volume"
            
        display.clear_buffers()
        display.draw_text( 46, 0, "RADIO", bally )
        display.draw_text( 22, 22, "%5.1f" % current_frequency + "FM", rototron )
        
    if mode_global == "volume":
        display.clear_buffers()
        if (toggled_up):
            volume_change("up")
            toggled_up = 0
            
        if (toggled_down):
            volume_change("down")
            toggled_down = 0
        
        display.draw_text( 46, 0, "VOLUME", bally )
        display.draw_bitmap("unmute_perfect.mono", 20, 22, 24, 24, True, 0)
        display.draw_text( 64, 22, str(current_volume), rototron )
        display.present()
        
        if (toggled_snooze):
            run_radio_menu()
            mode_global = "radio"
            toggled_snooze = 0
           
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
        

                
                