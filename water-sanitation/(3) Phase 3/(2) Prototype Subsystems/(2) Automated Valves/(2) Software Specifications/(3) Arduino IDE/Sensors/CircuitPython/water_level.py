'''
ESC204 2024S Lab 3, Task D
Task: Take readings using a digital temperature/humidity sensor.
'''

import board
import busio
import time
import adafruit_am2320

# set up I2C protocol
i2c = busio.I2C(board.GP17, board.GP16)
dhtDevice = adafruit_am2320.AM2320(i2c)

# read values from AM2320 sensor every 2 seconds
# (with gap in between temp and humidity readings)
while True:
    try:
        # Print the values to the serial port
        water_level = dhtDevice.water_level
        time.sleep(0.5)
        print("Water level: {} ".format(water_level))

    except RuntimeError as error:
        # Errors happen fairly often, DHTs are hard to read,
        # just keep trying to run/power cycle Pico
        # If errors are persistent, increase sleep times
        # Replacing busio with bitbangio can also sometimes help
        print(error.args[0])

    time.sleep(1.5)
