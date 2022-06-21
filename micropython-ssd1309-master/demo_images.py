"""SSD1309 demo (images)."""
from time import sleep
from machine import Pin, SPI
from ssd1309 import Display

# Initialize I/O pins associated with the oled display SPI interface
spi_res = Pin(16) # res stands for reset; always be connected to SPI RX pin of the Pico; this is the MISO
spi_dc  = Pin(17) # dc stands for data/commonda; always be connected to SPI CSn pin of the Pico
spi_sck = Pin(18) # sck stands for serial clock; always be connected to SPI SCK pin of the Pico
spi_sda = Pin(19) # sda stands for serial data;  always be connected to SPI TX pin of the Pico; this is the MOSI
spi_cs  = Pin(20) # can be connected to any free GPIO pin of the Pico

#
# SPI Device ID can be 0 or 1. It must match the wiring. 
#
SPI_DEVICE = 0 # Because the peripheral is connected to SPI 0 hardware lines of the Pico

def test():
    """Test code."""
    spi = SPI( SPI_DEVICE, baudrate=10000000, sck=spi_sck, mosi=spi_sda )
    display = Display( spi, dc=spi_dc, cs=spi_cs, rst=spi_res )

    display.draw_bitmap("images/eyes_128x42.mono", 0, display.height // 2 - 21, 128, 42)
    display.present()
    sleep(5)

    display.clear_buffers()
    display.draw_bitmap("images/doggy_jet128x64.mono", 0, 0, 128, 64, invert=True)
    display.present()
    sleep(5)

    display.clear_buffers()
    display.draw_bitmap("images/invaders_48x36.mono", 0, 14, 48, 36, rotate=90)
    display.draw_bitmap("images/invaders_48x36.mono", 40, 14, 48, 36)
    display.draw_bitmap("images/invaders_48x36.mono", 92, 14, 48, 36, rotate=270)
    display.present()

    sleep(10)
    display.cleanup()
    print('Done.')


test()
