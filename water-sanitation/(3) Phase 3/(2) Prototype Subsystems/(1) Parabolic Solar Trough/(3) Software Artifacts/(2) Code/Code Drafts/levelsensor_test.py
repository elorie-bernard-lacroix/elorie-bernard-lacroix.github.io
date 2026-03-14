# stepper motor code :-)
import time
import board
import digitalio

# motor variables
tracking_delay = 0.03
other_delay = 0.05
steps = 0 # 200 steps = 360º, 100 steps = 180º

# set up pins for controlling stepper shaft direction and pulsing steps
step_pin = digitalio.DigitalInOut (board.GP1)
dirn_pin = digitalio.DigitalInOut (board.GP0)
step_pin.direction = digitalio.Direction.OUTPUT
dirn_pin.direction = digitalio.Direction.OUTPUT
step_pin.value = False
dirn_pin.value = False # False is CW, True is CCW

# configure the GPIO pin connected to the switch as a digital input
# switch.value = False when pressed, True when not pressed
switch = digitalio.DigitalInOut(board.GP15)
switch.direction = digitalio.Direction.INPUT
switch.pull = digitalio.Pull.UP # set internal pull-up resistor

# configure the GPIO pin connected to the button as a digital input
# button.value = False when pressed, True when not pressed
button = digitalio.DigitalInOut(board.GP16)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP # set internal pull-up resistor

# configure the GPIO pin connected to the LED as a digital output
led = digitalio.DigitalInOut(board.GP14)
led.direction = digitalio.Direction.OUTPUT

# configure the GPIO pin connected to the Arduino Nano as a digital input
# level.value = False when pressed, True when not pressed
level = digitalio.DigitalInOut(board.GP19)
level.direction = digitalio.Direction.INPUT
level.pull = digitalio.Pull.UP # set internal pull-up resistor

# initialize level variables
full = False

def check_level():
    global full
    if (level.value == False):
        full == True
    else:
        full == False

# main loop
while True:
    check_level()

    if (full == True): # go to zero if water level full
        print("full")
    else:
        print("not full")
    time.sleep(2)
