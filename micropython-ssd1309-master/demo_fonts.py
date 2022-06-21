"""SSD1309 demo (fonts)."""
from time import sleep
from machine import Pin, SPI
from xglcd_font import XglcdFont
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

    print("Loading fonts.  Please wait.")
    bally = XglcdFont('fonts/Bally7x9.c', 7, 9)
    rototron = XglcdFont('fonts/Robotron13x21.c', 13, 21)
    unispace = XglcdFont('fonts/Unispace12x24.c', 12, 24)
    wendy = XglcdFont('fonts/Wendy7x8.c', 7, 8)

    print("Drawing fonts.")

    text_height = bally.height
    display.draw_text(display.width, display.height // 2 - text_height // 2, "Bally", bally, rotate=180)

    text_width = rototron.measure_text("ROTOTRON")
    display.draw_text(display.width // 2 - text_width // 2, 0, "ROTOTRON", rototron)

    text_width = unispace.measure_text("Unispace")
    text_height = unispace.height
    display.draw_text(display.width // 2 - text_width // 2, display.height - text_height, "Unispace", unispace, invert=True)
        
    text_width = wendy.measure_text("Wendy")
    display.draw_text(0, display.height // 2 - text_width // 2, "Wendy", wendy, rotate=90)

    display.present()

    sleep(10)
    display.cleanup()
    print('Done.')


test()
