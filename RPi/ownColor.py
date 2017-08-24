import json
from neopixel import Color

def mapNum( x,  in_min,  in_max,  out_min,  out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

class ownColor(object):

    def __init__(self, red=0, green=0, blue=0):
        self.set_red(red)
        self.set_green(green)
        self.set_blue(blue)

    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                   sort_keys=True, indent=4)

    @staticmethod
    def load_from_json(obj):
        return ownColor(obj[0], obj[1], obj[2])

    @staticmethod
    def get_from_color(color):
        return [color.red, color.green, color.blue]

    @staticmethod
    def from_hsv(h, l=1, s=1):
        import colorsys
        rgb = colorsys.hsv_to_rgb(h, l, s)
        #rgb = colorsys.hls_to_rgb(h, l, s)
        return ownColor(int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))

    def to_range(self, max_):
        self.set_red(mapNum(self.get_red(), 0, 255, 0, max_))
        self.set_green(mapNum(self.get_green(), 0, 255, 0, max_))
        self.set_blue(mapNum(self.get_blue(), 0, 255, 0, max_))

    def to_json(self):
        return [self.red, self.green, self.blue]

    def equals(self, other_col):
        return self.red == other_col.red and self.green == other_col.green and self.blue == other_col.blue

    def from_json(self, obj):
        if type(obj).__name__ == "ownColor":
            return obj
        else:
            self.set_red(obj[0])
            self.set_green(obj[1])
            self.set_blue(obj[2])
            return self

    def get_red(self):
        return self.red

    def set_red(self, red):
        self.red = min(255, max(0, red))

    def get_green(self):
        return self.green

    def set_green(self, green):
        self.green = min(255, max(0, green))

    def get_blue(self):
        return self.blue

    def set_blue(self, blue):
        self.blue = min(255, max(0, blue))

    def to_color(self):
        return Color(self.red, self.green, self.blue)

    def to_hex(self):
        return "{0:02x}{1:02x}{2:02x}".format(self.red, self.green, self.blue)