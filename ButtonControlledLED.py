import machine
import utime

led_onboard = machine.Pin(25, machine.Pin.OUT)
led_ext = machine.Pin(15, machine.Pin.OUT)
button_in = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_DOWN)

led_ext.value(0)
led_onboard.value(0)

while True:
    if button_in.value() == 1:
        #led_ext.toggle()
        #led_onboard.toggle()
        #utime.sleep_ms(250)
        led_ext.value(1)
        utime.sleep(3)
        led_ext.value(0)