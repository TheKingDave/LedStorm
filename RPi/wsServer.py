#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import threading
import time
from datetime import datetime
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
import websocket
from Display import Display
import os.path
from Config import Config
from ownColor import ownColor
from Logger import Logger, LogLevel
from ColorCalc import ColorCalc
from Energy import Energy
import codecs
import Adafruit_BMP.BMP085 as BMP085

def map_num(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def loop_range(num, max_):
    return loop_range(num-max_, max_) if num > max_ else num

class ClockThread(threading.Thread):
    def __init__(self, running=True):
        threading.Thread.__init__(self)
        self.running = not running
        self.set_running(running)
        self.stoped = False
        self.colon = True
        self.secondCount = 0
        self.showClock = False
        self.sensor = BMP085.BMP085()

    def set_running(self, running):
        if self.running == running:
            return
        self.running = running
        if running:
            display.set_brightness(config.get_option("clock_brightness"))
        else:
            display.set_brightness(config.get_option("led_bright"))

    def stop(self):
        self.stoped = True

    def run(self):
        while not self.stoped:
            if self.running:
                if self.showClock:
                    show_str = datetime.now().strftime("%H:%M")

                else:
                    # ~ as replacement of °
                    show_str = "{0:0.1f}~".format(self.sensor.read_temperature())

                self.colon = not self.colon
                if not self.colon:
                    show_str = show_str.replace(":", " ").replace(".", " ")
                display.set_brightness(config.get_option("clock_brightness"))
                dis = display.string_to_display(show_str, config.get_option("clock_color"),
                                                config.get_option("clock_bg_color"))
                display.show(dis)
                self.secondCount += 1
                if self.secondCount >= 10:
                    self.showClock = not self.showClock
                    self.secondCount = 0
                time.sleep(1)
            else:
                time.sleep(0.1)

class KeepAlive(threading.Thread):

    def __init__(self, interval=30):
        threading.Thread.__init__(self)
        self.interval = interval
        self.running = True
        self.stoped = False
        self.lastRun = time.time()

    def set_running(self, running):
        self.running = running

    def stop(self):
        self.stoped = True

    def run(self):
        while not self.stoped:
            if self.running:
                if time.time() - self.lastRun > self.interval:
                    for client in clients:
                        client.sendMessage(unicode(json.dumps({"type": "keepAlive", "data": ""})))
                    self.lastRun = time.time()
                time.sleep(0.5)
            else:
                time.sleep(0.1)

class ClockColor(ColorCalc):

    def __init__(self, columns, extra):
        ColorCalc.__init__(self, columns, extra)
        display.set_brightness(config.get_option("clock_brightness"))
        time_str = datetime.now().strftime("%H:%M")
        self.dis = display.string_to_display(time_str, config.get_option("clock_color"),
                                                config.get_option("clock_bg_color"))

    def column_color(self, data, column):
        return ownColor(0, 0, 0)

    def pixel_color(self, column_color, row_on, column, row, pixel):
        return self.dis[pixel]


class RainbowColor(ColorCalc):

    def __init__(self, columns, extra):
        ColorCalc.__init__(self, columns, extra)
        if "hue" not in extra: extra["hue"] = 0
        self.hue_start = extra["hue"]/360.0
        self.hue_delta = 1.0/columns

    def column_color(self, data, column):
        hue = self.hue_start + (self.hue_delta*column)
        col = ownColor.from_hsv(loop_range(hue, 1.0))
        col.to_range(data)
        return col

class StartEndColor(ColorCalc):

    def __init__(self, columns, extra):
        ColorCalc.__init__(self, columns, extra)
        self.start_col = config.get_option("start_color")
        self.end_col = config.get_option("end_color")

    def column_color(self, data, column):
        red = map_num(data, 0, 255, self.start_col.get_red(), self.end_col.get_red())
        green = map_num(data, 0, 255, self.start_col.get_green(), self.end_col.get_green())
        blue = map_num(data, 0, 255, self.start_col.get_blue(), self.end_col.get_blue())
        col = ownColor(red, green, blue)
        col.to_range(data)
        return col

clientConnected = 0
clients = []

class WsServer(WebSocket):

    def __init__(self, server_, sock, address):
        WebSocket.__init__(self, server_, sock, address)
        self.connectionType = "none"

    def send_error(self, msg):
        error = {"type": "error", "data": msg}
        self.sendMessage(unicode(json.dumps(error)))

    def handleMessage(self):
        try:
            self.handle_message_intern()
        except Exception as e:
            self.send_error(e.message)
            log.log_error(e.message)
            log.log_error(e.args)
            log.log_error(self.data)

    def handle_message_intern(self):
        try:
            data = json.loads(self.data)
        except Exception as e:
            self.send_error("Could not parse JSON")
            log.log_error(self.data)
            log.log_error(e)
            return

        # check type
        if not "type" in data:
            self.send_error("Could not find key 'type' in json")
            return
        type_ = data["type"]

        # check if keep alive package
        if type_ == "keepAlive":
            return

        # check if there is data
        if not "data" in data:
            self.send_error("Could not find key 'data' in json")
            return

        # data to variable
        data = data["data"]

        # set connection type
        if type_ == "setConnectionType":
            self.set_connection_type(data)
            return

        # witch connections are allowed to change options
        allowed_option_change = ["data", "control", "display"]
        if self.connectionType in allowed_option_change:
            if type_ == "data":
                self.handle_data(data)
            elif type_ == "set_option":
                self.handle_set_option(data)
            elif type_ == "get_option":
                self.handle_get_option(data)
            else:
                self.cmd_not_found(type_)

    def cmd_not_found(self, cmd):
        self.send_error("Could not find commmand '" + str(cmd) + "' or cmd is not allowed by connection type.")

    def handle_get_option(self, data):
        if "option" not in data:
            self.send_error("Could not find key 'option'")
        value = config.get_save_object(data["option"])
        if "request_id" in data:
            self.sendMessage(unicode(json.dumps({"type": "reply", "data":
                {"option": value,
                 "reply_id": data["request_id"]}})))
        else:
            self.sendMessage(unicode(json.dumps({"type": "reply", "data":
                {"option": value}})))

    def handle_set_option(self, data):
        if "option" not in data:
            self.send_error("Could not find key 'option'")
        if "value" not in data:
            self.send_error("Could not find key 'value'")
        config.set_option(data["option"], config.set_save_object(data["option"], data["value"]))
        log.log(str(self.address) + ": Set option '" + str(data["option"] + "' to " + str(data["value"])))

    def set_connection_type(self, data):
        data = str(data)

        # type 'data' search for other client with connection type 'data'
        if data == "data":
            for client in clients:
                if client.connectionType == "data":
                    self.send_error("Could not change connection type. Someone already data.")
                    log.log_info(str(self.address) + ": Blocked to change connection type")
                    return

        if data == "data" or data == "control" or data == "display":
            if data == "data":
                power.set_power(True)
            elif self.connectionType == "data":
                power.set_power(False)
            self.connectionType = data
            log.log_info(str(self.address) + ": Changed connection type to " + str(data))
            if self.connectionType == "data":
                clockThread.set_running(False)
        else:
            self.send_error("Could not find connection type '" + data + "'.")

    def handle_data(self, data):
        clockThread.set_running(False)
        color_mode = config.get_option("color_mode")

        #if color_mode != data["color_mode"]:
        #    return

        music_data = data["music_data"]

        if color_mode == "rainbow":
            col_calc = RainbowColor
        else:
            col_calc = StartEndColor

        dis = []
        for i in range(config.get_option("led_count")):
            dis.append(ownColor(0, 0, 0))

        display_width = config.get_option("display_width")
        display_height = config.get_option("display_height")

        extra = data["extras"] if "extras" in data else dict()

        esp_col = ownColor(0, 0, 0)
        esp_max = 0

        col_calc = col_calc(display_width, extra)
        for i in range(display_width):
            cur_data = int(min(255, max(0, music_data[i])))
            height = max(0, min(display_height, map_num(cur_data, 0, 255, 0, display_height)))
            col_color = col_calc.column_color(cur_data, i)

            if(cur_data > esp_max):
                esp_max = cur_data
                esp_col = col_color

            for a in range(display_height):
                pixel = ((display_width - i) + (a * display_width)) * -1
                dis[pixel] = col_calc.pixel_color(col_color, a<=height, i, a, pixel)

        esp.send("#" + esp_col.to_hex())
        display.show(dis)

    def handleConnected(self):
        global clientConnected
        clientConnected += 1
        if clientConnected > config.get_option("max_allowed_clients"):
            log.info("Closed connection of client. Because of to many clients")
            self.close(1013, "Not more than " + str(config.get_option("max_allowed_clients")) + " clients allowed")
            return
        try:
            log.info(str(self.address) + ": connected")
        except Exception as e:
            log.error(e)
        clients.append(self)

    def handleClose(self):
        global clientConnected
        clientConnected -= 1
        log.log_info(str(self.address) + ": closed")
        if self.connectionType == "data":
            power.set_power(False)
            clockThread.set_running(True)
        clients.remove(self)

# End of classes

if __name__ == "__main__":
    log = Logger("log.txt", LogLevel.LOG, LogLevel.INFO, True, True)
    server = SimpleWebSocketServer("", 8000, WsServer)

    log.log("Load config")
    config = Config("config.json", False, False)

    config.set_option_handler("ownColor", ownColor.load_from_json, ownColor.get_from_color)
    config.set_option_types(["clock_color", "clock_bg_color", "start_color", "end_color"], "ownColor")
    config.add_not_saves(["led_count", "display_active"])

    # Setup default config settings
    config.set_default("max_allowed_clients", 5)                # Max allowed clients (controller, display, data)
    # Not implemented
    #config.set_default("threading_on", True)                    # If threading for data request should be turned on
    #config.set_default("threading_max_threads", 50)             # Max allowed data request threads
    config.set_default("clock_brightness", 1)                   # Clock brightness
    config.set_default("clock_color", ownColor(0, 0, 255))      # Clock digit color
    config.set_default("clock_bg_color", ownColor(0, 0, 0))     # Clock bg color
    config.set_default("display_width", 25)                     # Display width
    config.set_default("display_height", 8)                     # Display height
    config.set_default("start_color", ownColor(0, 255, 0))      # color mode start_end start color
    config.set_default("end_color", ownColor(255, 0, 0))        # color mode start_end end color
    config.set_option("color_mode", "start_end")                # Visulization color mode
    config.set_default("led_bright", 255)                       # LED strip brightness
    config.set_default("power_switch_pin", 23)                  # Power switch pin
    config.set_default("power_switch_invert", True)             # If power switch signal should be inverted
    config.set_default("led_pin", 18)                           # GPIO pin connected to the pixels (must support PWM!).
    config.set_default("led_freq", 800000)                      # LED signal frequency in hertz (usually 800khz)
    config.set_default("led_dma", 5)                            # DMA channel to use for generating signal (try 5)
    config.set_default("led_invert", False)                     # True to invert the signal (when using NPN transistor level shift)
    config.set_default("display_file", "display.json")          # File where display string->led convertion is saved
    config.load()
    config.save()
    config.auto_save = True

    # set runtime config
    config.set_option("display_active", True)                   # If display should be activated (only leds, display still work)

    # set constant options
    config.set_option("led_count", config.get_option("display_height") * config.get_option("display_width"))    # set led count
    config.add_not_saves(["led_count"])

    # Init power
    log.info("Init power")
    power = Energy(config.get_option("power_switch_pin"), config.get_option("power_switch_invert"))

    log.info("Load display file: " + str(config.get_option("display_file")))
    if not os.path.isfile(config.get_option("display_file")):
        log.log_error("Could not find " + str(config.get_option("display_file")))
        exit(1)

    #with open("display.json") as data_file:
    #    text_display = json.load(data_file)

    with open("display.json") as data_file:
        text_display = json.load(data_file)

    display = Display(config, text_display, server, log)

    clockThread = ClockThread(True)
    clockThread.start()

    keepAliveThread = KeepAlive(10)
    keepAliveThread.start()

    esp = websocket.WebSocket()
    esp.connect("ws://192.168.0.27:8080")
    esp.send("R")

    try:
        log.info("Start server")
        server.serveforever()
    except KeyboardInterrupt:
        log.info("Stopped by user")
        clockThread.stop()
        keepAliveThread.stop()
        clockThread.join()
        keepAliveThread.join()
    finally:
        del display
