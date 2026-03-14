# stepper motor code :-)
import time
import board
import digitalio

# motor variables
slow_delay = 0.1
fast_delay = 0.03
steps = 100 # 200 = 360º, 100 = 180º

# set up pins for controlling stepper shaft direction and pulsing steps
step_pin = digitalio.DigitalInOut (board.GP1) #A1
dirn_pin = digitalio.DigitalInOut (board.GP0)  #A0
step_pin.direction = digitalio.Direction.OUTPUT
dirn_pin.direction = digitalio.Direction.OUTPUT
step_pin.value = False
dirn_pin.value = False

# configure the GPIO pin connected to the switch as a digital input
switch = digitalio.DigitalInOut(board.GP15) 
switch.direction = digitalio.Direction.INPUT
switch.pull = digitalio.Pull.UP # set internal pull-up resistor

# configure the GPIO pin connected to the button as a digital input
button = digitalio.DigitalInOut(board.GP16) 
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP # set internal pull-up resistor

# switch.value = False when pressed, True when not pressed
# button.value = False when pressed, True when not pressed

# initialize switch and button variables
switch_pressed = True
button_pressed = True
switch_cooldown = -1 # for debouncing
button_cooldown = -1
debounce = 10 # debounce time

# state variable
state = 1 # 1 = down (zero), 2 = turning, 3 = up

# main loop
while True:
    if (switch_cooldown > -1 and switch_cooldown < debounce):
        switch_cooldown = switch_cooldown + 1
        
    if (switch.value == False): # if receives pressed signal
        if (switch_pressed == False): # if we were at unpressed state
            if (switch_cooldown > debounce):
                print("ls press")
                switch_cooldown = -1
                switch_pressed = True # go to pressed state
            elif (switch_cooldown == -1): # turn on cooldown if it wasn't already on
                switch_cooldown = 0
    else:
        if (switch_pressed == True): # if pressed -> unpressed
            if (switch_cooldown > debounce):
                print("ls release")
                switch_cooldown = -1
                switch_pressed = False # go to unpressed state
            elif (switch_cooldown == -1): # turn on cooldown if it wasn't already on
                switch_cooldown = 0
    
    # check if button has been pressed
    if (button.value == False):
        if (button_pressed == False):
            print("b press")
        button_pressed = True
    else:
        if (button_pressed == button.value):
            print("b release")
        button_pressed = False


while True:
    # run one revolution CCW (day)
    print("daytime (CW)")
    dirn_pin.value = True
    for i in range(steps):
        # pulse high to drive step
        step_pin.value = True
        time.sleep(1e-5)
        # bring low in between steps
        step_pin.value = False
        time.sleep(slow_delay)
        
    # pause before turning (just as added safety measure)
    print("Motor not spinning yet")
    time.sleep(5)
    # run one revolution CW

    print("nighttime reset (CCW)")
    dirn_pin.value = False
    for i in range(steps):
        # pulse high to drive step
        step_pin.value = True
        time.sleep(1e-5)
        # bring low in between steps
        step_pin.value = False
        time.sleep(fast_delay)
    
    step_pin.value = False # stop random motor movements
    dirn_pin.value = False