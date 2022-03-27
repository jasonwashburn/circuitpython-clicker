import usb_hid
import time
import board
import digitalio
import neopixel
import math
from rainbowio import colorwheel
from adafruit_hid.mouse import Mouse

RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)
WHITE = (255, 255, 255)
OFF = (0, 0, 0)

MAX_DELAY = 2.0
MIN_DELAY = .01

step = ((math.log(MAX_DELAY) - math.log(MIN_DELAY))/(9))
delays = [1.0] + [math.exp(math.log(MIN_DELAY) + level * step) for level in range(9, -1, -1)]

led = digitalio.DigitalInOut(board.D13)
led.switch_to_output()
pixels = neopixel.NeoPixel(board.NEOPIXEL, 10, brightness=0.1, auto_write=False)


left_button = digitalio.DigitalInOut(board.BUTTON_A)
left_button.switch_to_input(pull=digitalio.Pull.DOWN)
right_button = digitalio.DigitalInOut(board.BUTTON_B)
right_button.switch_to_input(pull=digitalio.Pull.DOWN)
switch = digitalio.DigitalInOut(board.SLIDE_SWITCH)
switch.switch_to_input(pull=digitalio.Pull.UP)  # Left is True, Right is False

m = Mouse(usb_hid.devices)


class AutoClicker:
    def __init__(self, speed):
        if 1 <= speed <= 10:
            self.speed = speed
        else:
            raise ValueError("Speed must be between 1 and 10.")
        self.on = False
        self.show_speed_lights(flash=True, delay=0.5)
        self.click_delay = self.set_delay(self.speed)

    def start(self):
        self.set_delay(self.speed)
        self.on = True

    def stop(self):
        self.on = False

    def set_delay(self, speed: int):
        if 1 <= speed <= 10:
            self.click_delay = delays[speed]
            print(f"Delay: {self.click_delay} seconds")
            return True
        else:
            return False

    def speed_up(self):
        if self.speed < 10:
            self.speed += 1
            self.set_delay(self.speed)
            self.show_speed_lights(flash=True)
        else:
            self.flash_warning()
            time.sleep(.25)
            self.show_speed_lights(flash=True, delay=0.5)
        print(f"Speed: {self.speed}")
        return self.speed

    def slow_down(self):
        if self.speed > 1:
            self.speed -= 1
            self.set_delay(self.speed)
            self.show_speed_lights(flash=True)
        else:
            self.flash_warning()
            time.sleep(.25)
            self.show_speed_lights(flash=True, delay=0.5)
        print(f"Speed: {self.speed}")
        return self.speed

    def set_lights(self, level):
        if 1 <= level <= 10:
            pixels.fill(OFF)
            for i in range(level):
                pixels[i] = GREEN
            pixels.show()
        else:
            pixels.show()
            
    def show_speed_lights(self, flash: bool, delay: float = 0.25):
        self.set_lights(self.speed)
        if flash == True:
            time.sleep(delay)
            pixels.fill(OFF)
            pixels.show()
            
    def flash_warning(self):
        for _ in range(2):
            pixels.fill(RED)
            pixels.show()
            time.sleep(.1)
            pixels.fill(OFF)
            pixels.show()
            time.sleep(.1)

clicker = AutoClicker(speed=1)
buttons = [left_button, right_button] 
button_actions = [clicker.slow_down, clicker.speed_up]

while True:
    if switch.value == False:
        clicker.start()
    else:
        clicker.stop()

    if clicker.on == True:
        led.value = True
        m.click(Mouse.LEFT_BUTTON)
        time.sleep(clicker.click_delay / 2)
        led.value = False
        time.sleep(clicker.click_delay / 2)

    else:
        for button in buttons:
            if button.value:
                button_index = buttons.index(button)
                button_actions[button_index]()
                #pixels.show()
                while button.value:
                    pass
                #pixels.fill(OFF)
                #pixels.show()
                
        time.sleep(0.05)
