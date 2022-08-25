from inspect import classify_class_attrs


class StyleMixin:
    def get_style(self, name, tags):
        if name=="background":
            return 0xffffff, 0
        if name=="me":
            return 0xff0000, 5
        cls = tags.get('class')
        if name=="waterway" or name=="water":
            return 0x0000ff, 0
        if name=="landcover":
            return 0x00ff00, 0
        if name=="landuse":
            return 0xeeeeee, 1
        if name=="mountain_peak" or name=="peak":
            return 0xaaaaaa, 5
        if name=="park":
            return 0x00fa00, 0
        if name=="boundary":
            return 0x000000, 1
        if name=="transportation":
            return 0xff0000, 3
        if name=="building":
            return 0x0000ff, 1
        if name=="water_name":
            return 0x000000, 3
        if name=="transportation_name":
            return 0x000000, 3
        if name=="place":
            return 0x000000, 3
        if name=="housenumber":
            return 0x000000, 3
        if name=="poi":
            return 0xff0000, 3
        if name=="aerodrome_label":
            return 0xff0000, 3
        print(name, tags)
        return 0x000000, 1