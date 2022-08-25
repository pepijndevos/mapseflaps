import minipb

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

class VectorMixin:
    "A mixin class that implements drawing vector tiles using other drawing primitives"
    scale = 0

    def parse_geometry(self, geom, curx=0, cury=0):
        idx = 0
        start = (curx, cury)
        while idx < len(geom):
            cmd = geom[idx]
            idx+=1
            id = cmd & 0x7
            count = cmd >> 3
            pcount = count*2 if id != 7 else 0
            param = [wire._vint_dezigzagify(v) for v in geom[idx:idx+pcount]]
            idx+=pcount
            if id == 1: # MoveTo
                start = curx+param[0], cury+param[1]
            if id == 1 or id == 2: # LineTo
                for i in range(count):
                    curx += param[i*2]
                    cury += param[i*2+1]
                    yield id, curx, cury
            if id == 7: # ClosePath
                yield id, start[0], start[1]
    
    def draw_layer(self, lx, ly, name, keys, values, features):
        while features:
            feature = features.pop()
            ft = feature['tags']
            type_ = feature['type']
            geometry = feature['geometry']
            del feature
            tags = {}
            for i in range(0, len(ft), 2):
                tags[keys[ft[i]]] = values[ft[i+1]]
            del ft
            it = self.parse_geometry(geometry, lx, ly)
            style = self.get_style(name, tags) + (0x000000, 18)
            if type_ == 1: #POINT
                for _, x, y in it:
                    self.draw_point(x, y, *style[:2])
            elif type_ == 2: #LINESTRING
                lastx = lx
                lasty = ly
                for cmd, x, y in it:
                    if cmd != 1: # not MoveTo
                        self.draw_line(lastx, lasty, x, y, *style[:2])
                    lastx = x
                    lasty = y
            elif type_ == 3: #POLYGON
                vert = []
                holes = []
                for cmd, x, y in it:
                    if cmd == 7: #ClosePath
                        holes.append(len(vert))
                    else:
                        vert.extend([x, y])
                self.draw_polygon(vert, holes, *style[:2])
            fname = tags.get('name')
            if fname:
                self.draw_text(x, y, fname, *style[2:4])


    def draw_tile(self, x, y, path):
        # problem: the tag keys and values come after the features
        # so either you draw the features as they come in without tags SUCH AS THEIR NAME!
        # or you accumulate all the features into RAM, which could be a big chunk of memory
        # or you read the file in two passes, which is already SUPER SLOW
        # lets read into RAM and hope for the best
        layer = None
        features = []
        geometry = []
        tags = []
        type_ = None
        keys = []
        values = []
        with open(path, 'rb') as f:
            for k, v in wire.decode(f):
                if k == ("layers", "name"):
                    layer = v
                elif k == ("layers", "features", "geometry"):
                    geometry.append(v)
                elif k == ("layers", "features", "tags"):
                    tags.append(v)
                elif k == ("layers", "features", "type"):
                    type_ = v
                elif k == ("layers", "features") and v == "__end__":
                    features.append({"tags": tags, "geometry": geometry, "type": type_})
                    geometry = []
                    tags = []
                elif len(k)==3 and k[0:2] == ("layers", "values"):
                    values.append(v)
                elif k == ("layers", "keys"):
                    keys.append(v)
                elif k == ("layers", "extent"):
                    assert self.tilesize == v>>self.scale
                elif k == ("layers",) and v == "__end__":
                    self.draw_layer(x, y, layer, keys, values, features)
                    keys.clear()
                    values.clear()
                    features.clear()
