#This code will be used to test the OLED display
from machine import Pin, SPI, I2C, Timer # SPI is a class associated with the machine library. 
import utime
import time
import gui_io

# The below specified libraries have to be included.
# ssd1309.py and ds3231_port.py must be saved on the Pico. 
from ssd1309 import Display # OLED driver library and the corresponding class Display
#from ds3231_port import DS3231 # RTC module driver library and the corresponding class DS3231
from DS3231micro import DS3231
from xglcd_font import XglcdFont # Fonts
import framebuf # Another library for the display.
from fm_radio import Radio

# Define columns and rows of the oled display. These numbers are the standard values.
# Already defined in the ssd1309 library
# SCREEN_WIDTH = 126 #number of columns #128 for ssd1306, 126 for ssd1309
# SCREEN_HEIGHT = 64 #number of rows

# Initialize I/O pins associated with the oled display SPI interface
spi_res = Pin(16) # res stands for reset; always be connected to SPI RX pin of the Pico; this is the MISO
spi_dc  = Pin(17) # dc stands for data/commonda; always be connected to SPI CSn pin of the Pico
spi_sck = Pin(18) # sck stands for serial clock; always be connected to SPI SCK pin of the Pico
spi_sda = Pin(19) # sda stands for serial data;  always be connected to SPI TX pin of the Pico; this is the MOSI
spi_cs  = Pin(20) # can be connected to any free GPIO pin of the Pico

# Initialize I/O pins associated with the DS3231 RTC Module I2C interface
i2c_scl = Pin(13, Pin.PULL_UP, Pin.OPEN_DRAIN)
i2c_sda = Pin(12, Pin.PULL_UP, Pin.OPEN_DRAIN)

# Initialize I/O pins associated with button inputs
button_snooze = Pin(0, Pin.IN, Pin.PULL_DOWN)
button_mode = Pin(1, Pin.IN, Pin.PULL_DOWN)
button_up = Pin(2, Pin.IN, Pin.PULL_DOWN)
button_down = Pin(3, Pin.IN, Pin.PULL_DOWN)


# Initialize I/O pins associated with LEDs
red_led = Pin( 21, Pin.OUT, Pin.PULL_DOWN )
green_led = Pin( 22, Pin.OUT, Pin.PULL_DOWN )

encoderA = Pin( 14, Pin.IN, Pin.PULL_UP )
encoderB = Pin( 15, Pin.IN, Pin.PULL_UP )

# State Variables
toggled_snooze = 0 # variable defining whether a button was toggled
toggled_mode = 0
toggled_up = 0
toggled_down = 0
currentState_of_button = 0
mode_global = "clock" #default display state is clock

# Radio Initializations
fm_radio = Radio( 101.9, 2, False ) #Initialize radio
mute = False
current_frequency = 101.9
current_volume = 2

# Constants
pressed = 1
released = 0

#
# SPI and I2C Device IDs can be 0 or 1. It must match the wiring.
#
SPI_DEVICE_ID = 0 # Because the display is connected to SPI 0 hardware lines of the Pico
I2C_DEVICE_ID = 0 # Because the RTC is connected to I2C 0 hardware lines of the Pico
I2C_ADDR_RTCM = 104 # Determined by running i2c.scan()

#
# initialize the SPI interface for the OLED display and I2C interface for RTC Module
#
oled_spi = SPI( SPI_DEVICE_ID, baudrate=10000000, sck=spi_sck, mosi=spi_sda )
rtcm_i2c = I2C( I2C_DEVICE_ID, scl=i2c_scl, sda=i2c_sda )
#
# Initialize the display object
#
display = Display( oled_spi, cs=spi_cs, dc=spi_dc, rst=spi_res )
ds3231 = DS3231(13, 12)

#
# Time Variables
#
clock_time_12 = 0
alarm_time_12 = 0
time_format = 24
#ds3231.setAlarm(0,0,0)
alarm_hr = ds3231.getAlarm1()[1] #hours #0
alarm_min = ds3231.getAlarm1()[2] #minutes #0
alarm_sec = ds3231.getAlarm1()[3] #seconds #0
alarm_time = ('{:02d}'.format(alarm_hr) + ":" + '{:02d}'.format(alarm_min))
#alarm_time_full = ('{:02d}'.format(alarm_hr) + ":" + '{:02d}'.format(alarm_min) + ":" + '{:02d}'.format(alarm_sec))

#
# Alarm Sounds
#
#Dictionary of notes and their corresponding frequencies
note_freq = {
    "C4":262,
    "D4":294,
    "E4":330,
    "R":1 # rest note, any value > 0 will work here
    }

#Each list item is a note and its duration
alarm_theme = [["C4", 0.2], ["D4", 0.2], ["E4", 0.2], ["R", 0.4]]

speaker = machine.PWM(machine.Pin(8))

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
    elif mode_global == "ringing alarm":
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
        ds3231.setHour(time_hr)
        ds3231.setMinutes(time_min)
    if top_text == "SET ALARM":
        alarm_time = time_str_obj
        alarm_hr = hr_obj
        alarm_min = min_obj
        ds3231.setAlarm1(1, alarm_hr, alarm_min)
        
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
                
#Function for creating alarm sounds using PWM
def play_note(note_name, duration):
    if note_name == "R":
        speaker.duty_u16(0)
        time.sleep(duration)
    else:
        speaker.duty_u16(int(65535/2))#set duty cycle of the PWM
        frequency = note_freq[note_name]
        speaker.freq(frequency)#send freq to Pin
        time.sleep(duration)
        speaker.duty_u16(0)#stop the PWM
        
def program_frequency():
    encoderA = Pin( 14, Pin.IN, Pin.PULL_UP )
    encoderB = Pin( 15, Pin.IN, Pin.PULL_UP )
    val_changed = False
    button_encoder = Pin(11, Pin.IN, Pin.PULL_UP)
    toggled_encoder = 0
    global current_frequency, display
    
    while toggled_encoder == 0:
        if val_changed == True:
            if encoderA.value()==1 and encoderB.value()==1:
                val_changed = False
        if val_changed == False:
            if encoderA.value() == 0:
                if encoderB.value()==1:
                    current_frequency-=0.1
                    val_changed = True
                if val_changed == False:
                    current_frequency +=0.1
                    val_changed = True
                        
        display.clear_buffers()
        display.draw_text( 16, 0, "SET FREQUENCY", bally )
        display.draw_text( 22, 22, "%5.1f" % current_frequency + "FM", rototron )
        display.present()
        
        if button_encoder.value() == 0:
            currentState_of_button = pressed
            while currentState_of_button == pressed:
                if button_encoder.value() == 1:
                    currentState_of_button = released
                    toggled_encoder = 1
                    
        
    fm_radio.SetFrequency(current_frequency)
    fm_radio.ProgramRadio()
    toggled_encoder = 0

#initially time has not been set by user
timeset = False
alarm_shut = False
red_led.value(1)
green_led.value(1)
#Main Loop
while ( True ):
    #localtime = utime.localtime()
    time_sec = ds3231.getSeconds() #localtime[5]
    if not timeset:
        time_hr = ds3231.getHour() #localtime[3]
        time_min = ds3231.getMinutes() #localtime[4]      
        clock_time = ('{:02d}'.format(time_hr) + ":" + '{:02d}'.format(time_min) + ":" '{:02d}'.format(time_sec))
    
    alarm_time_full = alarm_time + ":" + '{:02d}'.format(alarm_sec)
    if clock_time == alarm_time_full: #check if clock hours, mins and secs match alarm
        mode_global = "ringing alarm"
        
    # Clear the buffer
    display.clear_buffers()

    # Cycle through system states
    if mode_global == "clock":
        #Check fore time format
        if time_format == 24:
            display.draw_text( 46, 0, "CLOCK", bally )
            display.draw_text( 20, 22, clock_time, rototron )#
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
        #Check for time format
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
            
        if encoderA.value() == 0:
            program_frequency()
        
        
                        
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
           
    if mode_global == "ringing alarm":
        display.clear_buffers()
        display.draw_text( 28, 22, "WAKE UP", rototron )
        fm_radio.SetMute( 1 )
        fm_radio.ProgramRadio()
        #Replay alarm sound pattern
        for note in alarm_theme:
            play_note(note[0], note[1])
            if (toggled_snooze):
                mode_global = "snooze"
                toggled_snooze = 0
                break
            if (toggled_mode):
                mode_global = "clock"
                toggled_mode = 0
                break
    
    if mode_global == "snooze":
        Mute = 1
        if ( fm_radio.SetMute( Mute ) == True ):
            fm_radio.ProgramRadio()
        snooze_time = 10
        while snooze_time >= 0:
            display.clear_buffers()
            display.draw_text( 0, 0, "Snooze Time Remaining", bally )
            display.draw_text( 36, 22, str(snooze_time), rototron )
            utime.sleep(1)
            snooze_time -= 1
            display.present()
        mode_global = "ringing alarm"
            
        
#
# Transfer the buffer to the screen
#
    display.present()
    
#
# Detect buttons presses
#
    button_toggle_detect(button_snooze)
    button_toggle_detect(button_mode)
    button_toggle_detect(button_down)
    button_toggle_detect(button_up)
    
    #switch modes when mode button is clicked
    if toggled_mode == 1:
        print("MODE")
        switch_mode_global()
        toggled_mode = 0
        
        

                
                
