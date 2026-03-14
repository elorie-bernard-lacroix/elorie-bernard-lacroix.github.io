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

# initialize switch variables
switch_pressed = False
prev_switch_pressed = False
debounce = 0.2 # debounce time

# initialize button variables
button_pressed = False

# state/checker variables
state = 1 # 1 = down (zero), 2 = turning, 3 = up
at_zero = False
state_2_substate = 1 # 1 = go to zero, 2 = go CW, 3 = go CCW
going_up = False

# check if limit switch has been pressed
def check_switch():
    global switch_pressed
    if (switch.value == False):
        if (switch_pressed == switch.value):
            print("ls press")
        switch_pressed = True
    else:
        if (switch_pressed == switch.value):
            print("ls release")
        switch_pressed = False

def check_button():
    global state, button_pressed
    if (button_pressed == False and button.value == False): # if button is initially pressed
        button_pressed = True
        if (state == 3):
            state = 1
            print(state)
        else:
            state += 1
            print(state)
    elif (button.value): # if button is released
        button_pressed = False

def turn(direction, delay):
    global dirn_pin, step_pin
    if (direction == "CCW"):
        dirn_pin.value = True # go CCW
    else:
        dirn_pin.value = False # go CW

    # pulse high to drive step
    step_pin.value = True
    time.sleep(1e-5)

    # bring low in between steps
    step_pin.value = False
    time.sleep(delay)

def go_to_zero(delay):
    # always turn until switch triggered
    if (switch_pressed == False):
        turn("CCW", delay)

# main loop
while True:
    check_switch()
    check_button()

    if (state == 1): # stay down (at zero)
        led.value = False
        steps = 0
        state_2_substate = 0
        going_up = False
        go_to_zero(other_delay)
    elif (state == 2):
        led.value = True
        if (state_2_substate == 1 and switch_pressed == False): # if just got to state 2, go to zero until switch press
            go_to_zero(other_delay)
        elif (switch_pressed == True): # if switch pressed, go CW
            steps = -50 # zero is 50-step offset from -90˚ position
            state_2_substate = 2
            turn("CW", tracking_delay)
            steps = steps + 1
        else:
            if (steps < 0): # if at leftmost limit (-90˚), set up to go CW
                state_2_substate = 2
            elif (steps > 100): # if at rightmost limit (+90˚), set up to go CCW
                state_2_substate = 3

            if (state_2_substate == 2): # go CW
                turn("CW", tracking_delay)
                steps = steps + 1
            if (state_2_substate == 3): # go CCW
                turn("CCW", tracking_delay)
                steps = steps - 1

    elif (state == 3):
        led.value = False
        if (going_up == False and switch_pressed == False): # if just got to state 3, go to zero until switch press
            steps = 0
            go_to_zero(other_delay)
        elif (switch_pressed == True or steps < 100): # turn CW once zeroed until trough faces upward
            if (switch_pressed == True):
                steps = 0
            going_up = True
            turn("CW", other_delay)
            steps = steps + 1

    step_pin.value = False # remove unwanted motor movement
