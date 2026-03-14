# stepper motor code :-)
import time
import board
import digitalio

# motor variables
slow_delay = 0.05
fast_delay = 0.01
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

# initialize switch and button states
switch_pressed = True
button_pressed = True

# state variable
state = 1 # 1 = down (zero), 2 = turning, 3 = up

# main loop
while True:
    # check if limit switch has been pressed
    if (switch.value == False):
        if (switch_pressed == switch.value):
            print("ls press")
        switch_pressed = True
    else:
        if (switch_pressed == switch.value):
            print("ls release")
        switch_pressed = False
    
    # check if button has been pressed
    if (button.value == False):
        if (button_pressed == button.value):
            print("b press")
        button_pressed = True
    else:
        if (button_pressed == button.value):
            print("b release")
        button_pressed = False



# pause before turning (just as added safety measure)
print("Motor not spinning yet")
time.sleep (5)

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

    print("nighttime reset (CCW)") (reset)
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