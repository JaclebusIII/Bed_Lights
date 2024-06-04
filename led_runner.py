import asyncio
import numpy as np
from rpi_ws281x import PixelStrip, Color
from math import ceil, floor


# LED strip configuration:
LED_COUNT = 100
LED_PIN = 18
LED_FREQ_HZ = 800000
LED_DMA = 10
LED_BRIGHTNESS = 255
LED_INVERT = False
LED_CHANNEL = 0      

LIGHT_LEVEL_STEP = .03
SHIFT_STEP = 0.03

# colors (grb)
BLACK = np.array([0,0,0])
WHITE = np.array([255,255,255])
PURPLE = np.array([32,160,240])
RED = np.array([0,255,0])
LAMP = np.array([120,255,50])

MONITOR_PERIOD = .1

class LEDRunner:
    def __init__(self, input_queue: asyncio.Queue):
        self.input_queue = input_queue

        self.mode_num = 0
        self.light_modes = [
            self.night_time_mode,
            self.white_mode,
            self.kimmie_mode,
            self.sexy_mode,
            
        ]

        self.light_state = False
        self.light_level = 1.0

        self.shift = False
        self.shift_int = 0

        self.strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
        self.strip.begin()
    
    def _set_all(self, color: Color):
        for j in range(self.strip.numPixels()):
            self.strip.setPixelColor(j, color)
        self.strip.show()

    def _set_shift(self, color: Color):
        b_range = ceil(0 if self.shift_int < 0 else self.shift_int*self.strip.numPixels())
        t_range = floor(self.strip.numPixels() if self.shift_int > 0 else self.strip.numPixels() + self.shift_int*self.strip.numPixels())
        #print(f"{b_range}:{t_range}")
        for j in range(0, b_range):
            self.strip.setPixelColor(j, self.apply_level(BLACK))
        for j in range(b_range, t_range):
            self.strip.setPixelColor(j, color)
        for j in range(t_range, self.strip.numPixels()):
            self.strip.setPixelColor(j, self.apply_level(BLACK))
        self.strip.show()

    def process_queue(self, packet):
        if packet == "held":
            self.light_state = not self.light_state
        elif packet == "scroll_up":
            if self.shift:
                if self.shift_int < 1:
                    self.shift_int += SHIFT_STEP 
            else:
                if self.light_level < 1:
                    self.light_level += LIGHT_LEVEL_STEP
        elif packet == "scroll_down":
            if self.shift:
                if self.shift_int > -1:
                    self.shift_int -= SHIFT_STEP
            else:
                if self.light_level > 0:
                    self.light_level -= LIGHT_LEVEL_STEP
        elif packet == "double":
            self.mode_num = (self.mode_num + 1) % len(self.light_modes)
        elif packet == "press":
            self.shift = not self.shift


        self.draw_lights()

    def draw_lights(self):
        if self.light_state:
            self.light_modes[self.mode_num]()
        else:
            self._set_all(self.apply_level(BLACK))

    def night_time_mode(self):
        self._set_shift(self.apply_level(LAMP))

    def white_mode(self):
        self._set_shift(self.apply_level(WHITE))

    def kimmie_mode(self):
        self._set_shift(self.apply_level(PURPLE))

    def sexy_mode(self):
        self._set_shift(self.apply_level(RED))

    def apply_level(self, color):
        leveled_color = (color * self.light_level).astype(int)
        if any(color_channel < 0 for color_channel in leveled_color):
            leveled_color = [0,0,0]
        return Color(*leveled_color)
    
    async def run(self):
        while True:
            packet = await self.input_queue.get()

            self.input_queue.task_done()

            if packet is not None:
                self.process_queue(packet)
                    
            #sleep(MONITOR_PERIOD)

        print("LEDRunner is Stopped")

        self._set_all(BLACK)

