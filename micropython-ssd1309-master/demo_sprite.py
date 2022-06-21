"""SSD1309 demo (bouncing sprite)."""
from machine import Pin, SPI
from utime import sleep_us, ticks_us, ticks_diff
from ssd1309 import Display


class BouncingSprite(object):
    """Bouncing Sprite."""

    def __init__(self, path, w, h, screen_width, screen_height,
                 speed, display):
        """Initialize sprite.
        Args:
            path (string): Path of sprite image.
            w, h (int): Width and height of image.
            screen_width (int): Width of screen.
            screen_height (int): Width of height.
            size (int): Square side length.
            speed(int): Initial XY-Speed of sprite.
            display (SSD1351): OLED display object.
            color (int): RGB565 color value.
        """
        self.buf = display.load_sprite(path, w, h, invert=True)
        self.w = w
        self.h = h
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.display = display
        self.x_speed = speed
        self.y_speed = speed
        self.x = self.screen_width // 2
        self.y = self.screen_height // 2
        self.prev_x = self.x
        self.prev_y = self.y

    def update_pos(self):
        """Update sprite speed and position."""
        x = self.x
        y = self.y
        w = self.w
        h = self.h
        x_speed = abs(self.x_speed)
        y_speed = abs(self.y_speed)

        if x + w + x_speed >= self.screen_width:
            self.x_speed = -x_speed
        elif x - x_speed < 0:
            self.x_speed = x_speed

        if y + h + y_speed >= self.screen_height:
            self.y_speed = -y_speed
        elif y - y_speed <= 0:
            self.y_speed = y_speed

        self.prev_x = x
        self.prev_y = y

        self.x = x + self.x_speed
        self.y = y + self.y_speed

    def draw(self):
        """Draw sprite."""
        x = self.x
        y = self.y
        prev_x = self.prev_x
        prev_y = self.prev_y
        w = self.w
        h = self.h
        x_speed = abs(self.x_speed)
        y_speed = abs(self.y_speed)

        # Determine direction and remove previous portion of sprite
        if prev_x > x:
            # Left
            self.display.fill_rectangle(x + w, prev_y, x_speed, h, invert=True)
        elif prev_x < x:
            # Right
            self.display.fill_rectangle(x - x_speed, prev_y, x_speed, h, invert=True)
        if prev_y > y:
            # Upward
            self.display.fill_rectangle(prev_x, y + h, w, y_speed, invert=True)
        elif prev_y < y:
            # Downward
            self.display.fill_rectangle(prev_x, y - y_speed, w, y_speed, invert=True)

        self.display.draw_sprite(self.buf, x, y, w, h)
        self.display.present()

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
    """Bouncing sprite."""
    try:
        # Baud rate of 14500000 seems about the max
        spi = SPI(SPI_DEVICE, baudrate=10000000, sck=spi_sck, mosi=spi_sda)
        display = Display(spi, dc=spi_dc, cs=spi_cs, rst=spi_res)
        display.clear()

        # Load sprite
        saucer = BouncingSprite('images/saucer_48x26.mono',
                              48, 26, 128, 64, 1, display)

        while True:
            timer = ticks_us()
            saucer.update_pos()
            saucer.draw()
            # Attempt to set framerate to 30 FPS
            timer_dif = 33333 - ticks_diff(ticks_us(), timer)
            if timer_dif > 0:
                sleep_us(timer_dif)

    except KeyboardInterrupt:
        display.cleanup()


test()