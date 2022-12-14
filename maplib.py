import math
import os
try:
    import requests
except ImportError:
    pass
try:
    import urequests as requests
except ImportError:
    pass
try:
    import adafruit_requests
    import wifi
    import socketpool
    import ssl
    pool = socketpool.SocketPool(wifi.radio)
    requests = adafruit_requests.Session(pool, ssl.create_default_context())
except ImportError:
    pass

# some circuitpython don't have hyperbolics but do have half a numpy
if hasattr(math, 'sinh') and hasattr(math, 'asinh'):
    sinh = math.sinh
    asinh = math.asinh
else:
    from ulab.numpy import asinh, sinh

def exists(filename):
    try:
        os.stat(filename)
        return True
    except OSError:
        return False

def deg2xy(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = (lon_deg + 180.0) / 360.0 * n
    ytile = (1.0 - asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n
    return (xtile, ytile)

def deg2num(lat_deg, lon_deg, zoom):
    return [int(x) for x in deg2xy(lat_deg, lon_deg, zoom)]

def deg2rem(lat_deg, lon_deg, zoom):
    return [x%1 for x in deg2xy(lat_deg, lon_deg, zoom)]

def num2deg(xtile, ytile, zoom):
  n = 2.0 ** zoom
  lon_deg = xtile / n * 360.0 - 180.0
  lat_rad = math.atan(sinh(math.pi * (1 - 2 * ytile / n)))
  lat_deg = math.degrees(lat_rad)
  return (lat_deg, lon_deg)

def tilesize(lat_deg, lon_deg, zoom):
    xtile, ytile = deg2num(lat_deg, lon_deg, zoom)
    lat1, lon1 = num2deg(xtile, ytile, zoom)
    lat2, lon2 = num2deg(xtile+1, ytile+1, zoom)
    return lat1-lat2, lon2-lon1
    
def assure_dir(path):
    for i in range(3, 0, -1):
        try:
            seg = path.rsplit('/', i)[0]
            os.mkdir(seg)
        except OSError:
            pass

class Mapview:
    tilesize = 256
    width = 800
    height = 600
    treshold = 5
    urltmpl = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
    pathtmpl = "tiles/{z}/{x}/{y}.png"
    zoom = 18
    lat = 52
    lon = 6
    gps = None
    tracking = True # view tracking GPS location

    def signal_busy(self):
        "Indicate to the user heavy lifting is going on"
        print("Busy")

    def signal_error(self):
        "Indicate to the user the heavy lifting failed"
        print("Error")
    
    def signal_done(self):
        "Indicate to the user heavy lifting is done"
        print("Done")


    def get_tile(self, x, y):
        path = self.pathtmpl.format(z=self.zoom, x=x, y=y)
        if exists(path):
            print("sd:", path)
            return path
        else:
            url = self.urltmpl.format(z=self.zoom, x=x, y=y)
            print("wifi:", url)
            try:
                res = requests.get(url, headers={"User-Agent": "Mapseflaps"})
            except Exception as e:
                print(e)
                return
            if res.status_code == 200:
                assure_dir(path)
                with open(path, 'wb') as f:
                    f.write(res.content)
                return path
            else:
                print(res.text)

    def draw_tile(self, x, y, path):
        "Draw tile data to the screen. Path can be png, mvt, ???, or None"
        raise NotImplementedError()
    
    def draw_chrome(self):
        print("(C) OpenMapTiles (C) OpenStreetMap contributors")

    def draw_map(self):
        try:
            self.signal_busy()
            color, _ = self.get_style("background", {})
            self.draw_fill(color)
            mid_x, mid_y = deg2num(self.lat, self.lon, self.zoom)
            my_x, my_y = deg2rem(self.lat, self.lon, self.zoom)
            size = self.tilesize
            left_x = int(self.width/2-my_x*size)
            top_y = int(self.height/2-my_y*size)
            right_x = int(self.width/2+(1-my_x)*size)
            bot_y = int(self.height/2+(1-my_y)*size)
            ty = math.ceil(top_y/size)
            by = math.ceil((self.height-bot_y)/size)
            lx = math.ceil(left_x/size)
            rx = math.ceil((self.width-right_x)/size)

            for dx in range(-lx, rx+1):
                for dy in range(-ty, by+1):
                    tile = self.get_tile(mid_x+dx, mid_y+dy)
                    scr_x = int(self.width/2+(dx-my_x)*size)
                    scr_y = int(self.height/2+(dy-my_y)*size)
                    self.draw_tile(scr_x, scr_y, tile) # can be None

            color, size = self.get_style("me", {})
            self.draw_point(self.width//2, self.height//2, color, size)
            self.draw_chrome()
            self.flush()
            self.signal_done()
        except Exception as e:
            print(e)
            self.signal_error()

    def update(self):
        if self.gps:
            self.gps.update()
            if self.tracking and self.gps.has_fix:
                curx, cury = deg2xy(self.lat, self.lon, self.zoom)
                newx, newy = deg2xy(self.gps.latitude, self.gps.longitude, self.zoom)
                dist = math.sqrt((curx-newx)**2 + (cury-newy)**2)*self.tilesize
                if dist > self.treshold:
                    self.lat = self.gps.latitude
                    self.lon = self.gps.longitude
                    self.draw_map()

    def zoom_in(self, pressed):
        if pressed:
            self.zoom += 1
            self.draw_map()

    def zoom_out(self, pressed):
        if pressed:
            self.zoom -= 1
            self.draw_map()

    def move_up(self, pressed):
        if pressed:
            self.lat += tilesize(self.lat, self.lon, self.zoom)[0]/self.tilesize*self.height/4
            self.tracking = False
            self.draw_map()

    def move_down(self, pressed):
        if pressed:
            self.lat -= tilesize(self.lat, self.lon, self.zoom)[0]/self.tilesize*self.height/4
            self.tracking = False
            self.draw_map()

    def move_left(self, pressed):
        if pressed:
            self.lon -= tilesize(self.lat, self.lon, self.zoom)[1]/self.tilesize*self.width/4
            self.tracking = False
            self.draw_map()

    def move_right(self, pressed):
        if pressed:
            self.lon += tilesize(self.lat, self.lon, self.zoom)[1]/self.tilesize*self.width/4
            self.tracking = False
            self.draw_map()

    def track(self, pressed):
        if pressed:
            self.tracking = True
            self.draw_map()

if __name__ == "__main__":
    m = Mapview()
    m.draw_map()