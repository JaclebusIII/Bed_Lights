from powermate import PowerMate
import asyncio

button_queue = asyncio.Queue(maxsize=5)

HOLD_TIME = 2
DOUBLE_THRESH = .2
MONITOR_PERIOD = .05

class ButtonController:
  def __init__(self, output_queue: asyncio, loop):
    self.output_queue = output_queue
    self.loop = loop

    self.setup_powermate()

    self.button_start_time = 0
    self.button_last_pressed = 0
    self.button_state = False
    self.button_held = False

  def setup_powermate(self):
    paths = PowerMate.enumerate()
    if not paths:
      print('No PowerMates detected')
      raise IOError
    else:
      self.powermate = PowerMate(
        paths[0],
        turn_callback=on_turn,
        button_callback=on_button,
        loop=self.loop
      )

    if self.powermate is None:
      print("Error Initializinf powermate")
      raise IOError
    
    self.powermate.set_led_solid(brightness=0)

  def get_loop(self):
    return self.loop

  def process_packet(self, packet):
    if packet is not None:
      #print(packet)
      if packet[0] == "button":
        if packet[1]: 
          #print("Button Pressed")
          self.output_queue.put_nowait("press")

          self.button_state = True
          self.button_start_time = packet[2]

          if packet[2] - self.button_last_pressed <= DOUBLE_THRESH:
            #print("Double Press")
            self.output_queue.put_nowait("double")

          self.button_last_pressed = packet[2]
        else:
          #print("Button unPressed")

          self.button_state = False
          self.button_held = False
      else:
        if packet[1] < 0:
          self.output_queue.put_nowait("scroll_down")
        else:
          self.output_queue.put_nowait("scroll_up")
    else:
      if self.button_state and not self.button_held:
        if asyncio.get_event_loop().time() - self.button_start_time >= HOLD_TIME:
          #print("Button has been held")
          self.output_queue.put_nowait("held")

          self.button_held = True

  async def button_monitor(self):
    while True:
      try:
        packet = button_queue.get_nowait()
      except asyncio.QueueEmpty:
        packet = None
      
      self.process_packet(packet)
      
      await asyncio.sleep(MONITOR_PERIOD)
     
def on_turn(amount):
  global button_queue

  packet = ("scroll", amount, asyncio.get_event_loop().time())

  try:
    button_queue.put_nowait(packet)
  except asyncio.QueueFull:
    pass

def on_button(pressed):
  global button_queue

  packet = ("button", pressed, asyncio.get_event_loop().time())

  try:
    button_queue.put_nowait(packet)
  except asyncio.QueueFull:
    pass