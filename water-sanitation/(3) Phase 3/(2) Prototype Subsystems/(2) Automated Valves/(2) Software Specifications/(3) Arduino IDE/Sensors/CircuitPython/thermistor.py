'''
ESC204 2024S Prototyping
Task: Take readings using a thermistor.
'''

import time
import board
import analogio

# set display to show either:
INT_MODE = 0        # ADC output representative integer
VOLT_MODE = 1       # the voltage that it represents
mode = INT_MODE

# always 0xff (in hex) according to: https://learn.adafruit.com/
# circuitpython-basics-analog-inputs-and-outputs/
# analog-to-digital-converter-inputs
ADC_HIGH = 65535

# set up thermistor as analog input over analog pin A0
thermistor_pin = board.GP26_A0
thermistor = analogio.AnalogIn(thermistor_pin)

# show reference voltage (logic high, 3.3V) and the
# corresponding analog integer value
ADC_REF = thermistor.reference_voltage
print("ADC reference voltage: {}".format(ADC_REF))
print("ADC high voltage integer value: {}".format(ADC_HIGH))

# convert ADC input value back to voltage
def adc_to_voltage(adc_value):
    return  ADC_REF * (float(adc_value)/float(ADC_HIGH))

# take readings from thermistor
while True:
    if mode == INT_MODE: # read adc value and print
        print((thermistor.value,))
    else: # convert to voltage
        print((adc_to_voltage(thermistor.value),))

    time.sleep(0.5)
