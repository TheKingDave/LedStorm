import json
from neopixel import *
from ownColor import ownColor
from Logger import Logger, LogLevel


class Display(object):

    def __init__(self, config, letters, ws_server=None, log=Logger(None, LogLevel.NOTHING, LogLevel.INFO, False)):
        self.config = config
        self.letters = letters
        self.ws_server = ws_server
        self.log = log
        self.brightness = 111
        self.log.info("Init LED Strip")
        self.strip = Adafruit_NeoPixel(
            config.get_option("led_count"),
            config.get_option("led_pin"),
            config.get_option("led_freq"),
            config.get_option("led_dma"),
            config.get_option("led_invert"),
            config.get_option("clock_brightness")
        )
        self.strip.begin()
        self.log.info("LED Strip initiated")

    def set_brightness(self, bright):
        bright = min(255, max(0, bright))
        if bright == self.brightness:
            return
        self.brightness = bright
        self.strip.setBrightness(bright)
        self.strip.show()

    def string_to_display(self, text="", color=ownColor(0, 0, 255), bg_color=ownColor(0, 0, 0)):
        ret = []
        height = self.letters["height"]
        from_top = (self.config.get_option("display_height")-height) / 2
        for i in range(from_top*self.config.get_option("display_width")):
            ret.append(bg_color)

        for i in range(height):
            line = []
            for l in text:
                for a in self.letters["letters"][l][i]:
                    if a == 0:
                        line.append(bg_color)
                    else:
                        line.append(color)
                line.append(bg_color)
            line = self.center(line, bg_color)
            ret.extend(line)

        while len(ret) < self.config.get_option("led_count"):
            ret.append(bg_color)

        return ret

    def center(self, line, bg_color=ownColor(0, 0, 0)):
        ret = []
        for i in range((self.config.get_option("display_width")-len(line)) /2):
            ret.append(bg_color)
        ret.extend(line)
        while len(ret) < self.config.get_option("display_width"):
            ret.append(bg_color)
        return ret

    def __del__(self):
        for led in range(self.strip.numPixels()):
            self.strip.setPixelColor(led, ownColor(0, 0, 0).to_color())
        self.strip.show()

    def show(self, display):
        if self.strip.numPixels() != len(display):
            return

        if self.config.get_option("display_active") is True:
            for i in range(len(display)):
                self.strip.setPixelColor(self.strip.numPixels() - i - 1, display[i].to_color())
        else:
            for i in range(len(display)):
                self.strip.setPixelColor(i, ownColor(0, 0, 0).to_color())

        self.strip.show()

        if self.ws_server is not None:
            json_data = None
            for conn, client in self.ws_server.connections.items():
                if client.connectionType == "display":
                    if json_data is None:
                        json_data = []
                        for i in reversed(range(len(display))):
                            json_data.append(display[i].to_json())

                    client.sendMessage(unicode(json.dumps({"type": "data", "data": json_data})))

    def print_display(self, dis, bg_col=ownColor(0, 0, 0)):
        str_ = ""
        for i in range(len(dis)):
            if i % self.config.get_option("display_width") == 0:
                str_ += "\n"
            str_ += " " + ("0" if dis[i].equals(bg_col) else "1")
        self.log.info(str_)
