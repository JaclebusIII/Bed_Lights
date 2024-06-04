import asyncio
from led_runner import LEDRunner
from button_controller import ButtonController

async def main():
  print("Light Controller Started")

  loop = asyncio.get_event_loop()
  tasks = []
  q = asyncio.Queue()

  button_runner = ButtonController(q, loop)
  LED_runner = LEDRunner(q)

  tasks.append(loop.create_task(LED_runner.run()))
  tasks.append(loop.create_task(button_runner.button_monitor()))

  try:
    await asyncio.gather(*tasks)
  except KeyboardInterrupt:
    print("Stopping")
    LED_runner.cancel()
    pass


if __name__ == "__main__":
  asyncio.run(main())
