import wifi
import display
import buttons
from maplib import Mapview
# from mvt import VectorMixin


class BadgeteamMapview(Mapview):
    width=320
    height=240
    pathtmpl = "/sd/osmtiles/{z}/{x}/{y}.png"

    def draw_tile(self, x, y, path):
        print("draw png", x, y, path)
        with open(path, 'rb') as f:
            display.drawPng(x, y, f.read())

    def draw_point(self, x, y, name, tags):
        display.drawCircle(x, y, 5, 0, 360, True, 0xff0000)
        if "name" in tags:
            display.drawText(x, y, tags["name"], 0x000000, "7x5")

    def draw_line(self, x1, y1, x2, y2, name, tags):
        display.drawLine(x1, y1, x2, y2, 0x0000ff)
    
    def draw_fill(self, color):
        print("fill")
        display.drawFill(color)

    def flush(self):
        display.flush()
        print("flush")

# class PygameVectorMapview(VectorMixin, PygameMapview):
#     urltmpl = "https://api.maptiler.com/tiles/v3-openmaptiles/{z}/{x}/{y}.pbf?key=dMxOGgHTyghLg71Ok4wG"
#     pathtmpl = "vtiles/{z}/{x}/{y}.pbf"
#     zoom = 14
#     tilesize = 4096

wifi.connect()
# m = PygameVectorMapview()
m = BadgeteamMapview()

# m.draw_map()

buttons.attach(buttons.BTN_A, m.zoom_in)
buttons.attach(buttons.BTN_B, m.zoom_out)
buttons.attach(buttons.BTN_UP, m.move_up)
buttons.attach(buttons.BTN_DOWN, m.move_down)
buttons.attach(buttons.BTN_LEFT, m.move_left)
buttons.attach(buttons.BTN_RIGHT, m.move_right)
