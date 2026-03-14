import board
import digitalio

# Configure the GPIO pin connected to the LED as a digital output
led = digitalio.DigitalInOut(board.GP14)
led.direction = digitalio.Direction.OUTPUT

# Configure the GPIO pin connected to the button as a digital input
button = digitalio.DigitalInOut(board.GP16)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP # Set internal pull-up resistor

# button.value = False when pressed
# led turns on when led.value = True
button_pressed = False
state = 1 # 1 is off, 2 is R and B on, 3 is all lights on
        
# Loop so the code runs continuously
while True:
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
    if (state == 1):
        led.value = False
    elif (state == 2):
        led.value = True
    else:
        led.value = False