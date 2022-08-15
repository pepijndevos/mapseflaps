import minipb
import zlib
import time
import display

value = (('string_value', 'U'),
         ('float_value', 'f'),
         ('double_value', 'd'),
         ('int_value', 't'),
         ('uint_value', 'T'),
         ('sint_value', 'z'),
         ('bool_value', 'b'))

feature = (('id', 'T'),
           ('tags', '#T'),
           ('type', 't'),
           ('geometry', '#T'))

layer = (('name', '*U'),
         ('features', '+[', feature, ']'),
         ('keys', '+U'),
         ('values', '+[', value, ']'),
         ('extent', 'T'),
         ('_', 'x9'),
         ('version', '*T'))

tile = (('_', 'x2'), ('layers', '+[', layer, ']'))

wire = minipb.IterWire(tile)

def unpack(path):
    with open(path, 'rb') as f:
        # adjust between 16+ 8..15 to allocate buffer
        raw = zlib.DecompIO(f, 16+12)
        yield from wire.decode(raw)

def draw_feature(feat, curx=0, cury=0):
    scale = 5
    idx = 0
    start = (curx, cury)
    while idx < len(feat):
        cmd = feat[idx]
        idx+=1
        id = cmd & 0x7
        count = cmd >> 3
        if id == 1: # MoveTo
            pcount = count*2
            param = [wire._vint_dezigzagify(v) for v in feat[idx:idx+pcount]]
            idx+=pcount
            start = curx+param[0], cury+param[1]
            # print("MoveTo", *param)
            for i in range(count):
                curx += param[i*2]
                cury += param[i*2+1]
        elif id == 2: # LineTo
            pcount = count*2
            param = [wire._vint_dezigzagify(v) for v in feat[idx:idx+pcount]]
            idx+=pcount
            # print("LineTo", *param)
            for i in range(count):
                dx = param[i*2]
                dy = param[i*2+1]
                display.drawLine(curx>>scale, cury>>scale, curx+dx>>scale, cury+dy>>scale, 0x000000)
                curx += dx
                cury += dy
        elif id == 7: # ClosePath
            # print("ClosePath")
            display.drawLine(curx>>scale, cury>>scale, start[0]>>scale, start[1]>>scale, 0x000000)

def draw_tile(path, curx=0, cury=0):
    feature = []
    for k, v in unpack(path):
        pass
        if k == ("layers", "features") and v == "__start__":
            feature = []
        if k == ("layers", "features") and v == "__end__":
            draw_feature(feature, curx, cury)
        elif k == ("layers", "features", "geometry"):
            feature.append(v)

# with open('/home/pepijn/Downloads/5384.pbf.2', 'rb') as f:
#     ref = refwire.decode(f)
# print(ref)
display.drawFill(0xffffff)
start = time.time()
draw_tile('/sd/vtiles/19/272100/172664.pbf')
draw_tile('/sd/vtiles/19/272101/172664.pbf', curx=4096)
print(time.time()-start)
display.flush(display.FLAG_LUT_NORMAL)