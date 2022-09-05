import os
import sdcardio
import storage
import time
import board
import displayio
import bitmaptools
import png
import wifi
from secrets import secrets
from maplib import Mapview
from adafruit_display_shapes.circle import Circle

print("hello world")

sd = sdcardio.SDCard(board.SPI(), board.D5)
vfs = storage.VfsFat(sd)
storage.mount(vfs, '/sd')

print("SD mounted")

wifi.radio.connect(secrets["ssid"], secrets["password"])

print("wifi connected")

_START_SEQUENCE = (
    b"\x00\x81\x05\x0e"  # soft reset, delay 5ms
    b"\xe5\x01\x19" # set input temperature
    b"\xe0\x01\x02" # set active temperature?
    b"\x00\x02\x0f\x89" # set psr
    b"\04\x80\xc8" # power on an wait 200ms
)

_STOP_SEQUENCE = (
    b"\x02\x80\xf0"  # Power off
)

# pylint: disable=too-few-public-methods
class PervasiveDisplay(displayio.EPaperDisplay):
    """IL0398 driver"""

    def __init__(self, bus: displayio.FourWire, **kwargs) -> None:

        width = kwargs["width"]
        height = kwargs["height"]
        super().__init__(
            bus,
            _START_SEQUENCE,
            _STOP_SEQUENCE,
            **kwargs,
            ram_width=width,
            ram_height=height,
            busy_state=False,
            black_bits_inverted=True,
            always_toggle_chip_select=True,
            write_black_ram_command=0x10,
            write_color_ram_command=0x13,
            refresh_display_command=0x12,
        )

displayio.release_displays()

# This pinout works on a Feather M4 and may need to be altered for other boards.
spi = board.SPI()  # Uses SCK and MOSI
epd_cs = board.D9
epd_dc = board.D10
epd_reset = board.D12
epd_busy = board.D11

display_bus = displayio.FourWire(
    spi, command=epd_dc, chip_select=epd_cs, reset=epd_reset, baudrate=1000000
)
time.sleep(1)

print("Creating display")


class DisplayioMapview(Mapview):
    width=480
    height=176
    pathtmpl = "/sd/tiles/{z}/{x}/{y}.png"
    urltmpl = "http://vps.pepijndevos.nl:8181/styles/toner/{z}/{x}/{y}.png"
    tilesize = 64
    lat = 52.370216
    lon = 4.895168
    zoom = 14

    def __init__(self, display_bus, busy_pin):
        self.display = PervasiveDisplay(
            display_bus,
            width=self.width,
            height=self.height,
            rotation=270,
            # highlight_color=0xFF0000,
            busy_pin=busy_pin,
        )
        self.group = displayio.Group()

    def get_style(self, name, tags):
        if name=="background":
            return 0xffffff, 0
        if name=="me":
            return 0xff0000, 5

    def draw_tile(self, x, y, path):
        print("draw png", x, y, path)
        w, h, px, meta = png.Reader(filename=path).read_flat()
        numpal = len(meta['palette'])
        bm = displayio.Bitmap(w,h, numpal)
        bitmaptools.arrayblit(bm, px)
        pal = displayio.Palette(numpal)
        for i, p in enumerate(meta['palette']): pal[i] = p
        grid = displayio.TileGrid(bm, pixel_shader=pal, x=x, y=y)
        self.group.append(grid)

    def draw_point(self, x, y, color, size):
        self.group.append(Circle(x, y, size, fill=color))

    def draw_fill(self, color):
        print("fill")

    def flush(self):
        self.display.show(self.group)
        self.display.refresh()
        self.group = displayio.Group()
        print("flush")


m = DisplayioMapview(display_bus, epd_busy)
m.draw_map()