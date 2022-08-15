import math
import wifi
import urequests
import display
import buttons
import time
import os
import neopixel
from machine import UART
from adafruit_gps import GPS

urltmpl = "http://vps.pepijndevos.nl:8181/styles/toner/{z}/{x}/{y}.png"
pathtmpl = "/sd/tiles/{z}/{x}/{y}.png"

wifi.connect()
neopixel.enable()

def exists(filename):
    try:
        os.stat(filename)
        return True
    except OSError:
        return False

def deg2num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return (xtile, ytile)

def deg2rem(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = ((lon_deg + 180.0) / 360.0 * n) % 1
    ytile = ((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n) % 1
    return (int(xtile*64), int(ytile*64))

def assure_dir(path):
    for i in range(3, 0, -1):
        try:
            seg = path.rsplit('/', i)[0]
            os.mkdir(seg)
        except OSError:
            pass

def get_tile(x, y, zoom):
    path = pathtmpl.format(z=zoom, x=x, y=y)
    assure_dir(path)
    if exists(path):
        print("sd")
        with open(path, "rb") as f:
            return f.read()
    elif wifi.status():
        print("wifi")
        url = urltmpl.format(z=zoom, x=x, y=y)
        res = urequests.get(url, headers={"User-Agent": "ESP32 badge"})
        if res.status_code == 200:
            with open(path, 'wb') as f:
                f.write(res.content)
            return res.content
        else:
            print(res.text)
    with open("/media/alert.png", "rb") as f:
        return f.read()

def draw_map(lat, lon, zoom):
    global last_pos
    try:
        neopixel.send(bytes([0xf, 0x0, 0x0]))
        mid_x, mid_y = deg2num(lat, lon, zoom)
        my_x, my_y = deg2rem(lat, lon, zoom)
        tl_x = mid_x-2
        my_x += 128
        if my_y > 32:
            tl_y = mid_y
        else:
            tl_y = mid_y-1
            my_y += 64

        for dx in range(5):
            for dy in range(2):
                tile = get_tile(tl_x+dx, tl_y+dy, zoom)
                if tile:
                    display.drawPng(dx*64, dy*64, tile)

        display.drawText(0, display.height()-10, "(C) OpenMapTiles (C) OpenStreetMap contributors", 0, "7x5")
        display.drawCircle(my_x, my_y, 5, 0, 360, False, 0)
        display.flush(display.FLAG_LUT_GREYSCALE)
        neopixel.send(bytes([0x0, 0x0, 0x0]))
    except Exception as e:
        print(e)
        neopixel.send(bytes([0x0, 0xf, 0x0]))

zoom = 18
lat = 52
lon = 6

def zoom_in(pressed):
    global zoom
    if pressed:
        zoom += 1
        draw_map(lat, lon, zoom)

def zoom_out(pressed):
    global zoom
    if pressed:
        zoom -= 1
        draw_map(lat, lon, zoom)

def move_up(pressed):
    global lat
    if pressed:
        lat += 180/2**zoom
        draw_map(lat, lon, zoom)

def move_down(pressed):
    global lat
    if pressed:
        lat -= 180/2**zoom
        draw_map(lat, lon, zoom)

def move_left(pressed):
    global lon
    if pressed:
        lon -= 180/2**zoom
        draw_map(lat, lon, zoom)

def move_right(pressed):
    global lon
    if pressed:
        lon += 180/2**zoom
        draw_map(lat, lon, zoom)

# https://badge.team/docs/badges/sha2017/hardware/#add-ons
uart = UART(1, 9600, tx=33, rx=12)
gps = GPS(uart, True)

buttons.attach(buttons.BTN_A, zoom_in)
buttons.attach(buttons.BTN_B, zoom_out)
buttons.attach(buttons.BTN_UP, move_up)
buttons.attach(buttons.BTN_DOWN, move_down)
buttons.attach(buttons.BTN_LEFT, move_left)
buttons.attach(buttons.BTN_RIGHT, move_right)

draw_map(lat, lon, zoom)
while True:
    try:
        t = time.ticks_ms()
        while time.ticks_ms() < t+5000:
            gps.update()
            time.sleep(0.1)

        if gps.has_fix:
            print("Updating...")
            lat = gps.latitude
            lon = gps.longitude
            draw_map(lat, lon, zoom)
        else:
            print("No fix")
    except Exception as e:
        print(e)
        neopixel.send(bytes([0x0, 0xf, 0x0]))
