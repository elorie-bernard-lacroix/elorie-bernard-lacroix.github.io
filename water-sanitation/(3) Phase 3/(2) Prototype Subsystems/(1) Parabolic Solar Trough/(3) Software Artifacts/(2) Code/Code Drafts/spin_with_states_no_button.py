# stepper motor code :-)
import time
import board
import digitalio

# motor variables
slow_delay = 0.1
fast_delay = 0.03
steps = 100 # 200 = 360º, 100 = 180º

# set up pins for controlling stepper shaft direction and pulsing steps
step_pin = digitalio.DigitalInOut (board.GP1) 
dirn_pin = digitalio.DigitalInOut (board.GP0) 
step_pin.direction = digitalio.Direction.OUTPUT
dirn_pin.direction = digitalio.Direction.OUTPUT
step_pin.value = False
dirn_pin.value = False # False is CCW, True is CW

# configure the GPIO pin connected to the switch as a digital input
switch = digitalio.DigitalInOut(board.GP15) 
switch.direction = digitalio.Direction.INPUT
switch.pull = digitalio.Pull.UP # set internal pull-up resistor

# switch.value = False when pressed, True when not pressed

# initialize switch variables
switch_pressed = True
prev_switch_pressed = False
debounce = 0.2 # debounce time

# state/checker variables
state = 1 # 1 = down (zero), 2 = turning, 3 = up
at_zero = False
going_CW = False
gone_up = False

# check if limit switch has been pressed
def check_switch():
    global switch_pressed, prev_switch_pressed
    if (switch.value == False):
        
        if (switch_pressed == switch.value):
            print("ls press")
            #if (prev_switch_pressed == False):
            #    prev_switch_pressed = True
            
            switch_pressed = True
            return 1 # unpressed -> pressed 
            
        switch_pressed = True
    else:
        if (switch_pressed == switch.value):
            print("ls release")
            #if (prev_switch_pressed == True):
            #    prev_switch_pressed = False
            
            switch_pressed = False
            return 2 # pressed -> unpressed
            
        switch_pressed = False
    return 0

def turn(direction, delay):
    if (direction == "CCW"):
        dirn_pin.value = False # go CCW
    else:
        dirn_pin.value = True # go CW
    
    # pulse high to drive step
    step_pin.value = True
    time.sleep(1e-5)
    
    # bring low in between steps
    step_pin.value = False
    time.sleep(delay)

def go_to_zero():
    global fast_delay
    # always turn until switch triggered
    if (switch_pressed == False):
        turn("CCW", fast_delay)

# main loop
while True:
    press_change = check_switch()
    
    if (state == 1): # stay down (at zero)
        steps = 0
        going_CW = False
        gone_up = False
        go_to_zero()
    elif (state == 2):
        if (going_CW == False and switch_pressed == False): # if just got to state 2, go to zero until switch press
            go_to_zero()
        elif (switch_pressed == True or steps < 100): # turn CW once zeroed until rightmost limit (∆ = +180º)
            going_CW = True
            turn("CW", slow_delay)
            steps = steps + 1
        elif (steps >= 100): # if at rightmost limit, set up to go back
            steps = 0
            going_CW_3 = False
    elif (state == 3):
        if (gone_up == False and switch_pressed == False): # if just got to state 3, go to zero until switch press
            go_to_zero()
        elif (switch_pressed == True or steps < 50): # turn CW once zeroed until rightmost limit (∆ = +90º)
            going_CW_3 = True
            turn("CW", fast_delay)
            steps = steps + 1
        elif (steps >= 50): # if at rightmost limit, set up to go back
            steps = 0
            gone_up = True