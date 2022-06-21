"""SSD1309 demo (shapes)."""
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
    spi = SPI(SPI_DEVICE, baudrate=10000000, sck=spi_sck, mosi=spi_sda)
    display = Display(spi, dc=spi_dc, cs=spi_cs, rst=spi_res)

    display.draw_rectangle(1, 1, 30, 30)
    display.fill_rectangle(6, 6, 20,20)

    display.fill_circle(50, 16, 14)
    display.draw_circle(50, 16, 10, invert=True)

    coords = [[106, 0], [106, 60], [70, 11], [127, 30], [70, 49], [106, 0]]
    display.draw_lines(coords)

    display.fill_ellipse(16, 48, 15, 8)
    display.draw_ellipse(16, 48, 8, 15)

    display.fill_polygon(5, 50, 48, 8)
    display.draw_polygon(7, 50, 48, 15)

    display.draw_line(117, 63, 127, 53)
    display.draw_vline(127, 53, 10)
    display.draw_hline(117, 63, 10)

    display.present()

    sleep(10)
    display.cleanup()
    print('Done.')


test()
