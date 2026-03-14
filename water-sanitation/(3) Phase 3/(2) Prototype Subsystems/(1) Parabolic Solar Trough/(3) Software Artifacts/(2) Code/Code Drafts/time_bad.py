# stepper motor code :-)
import time
import board
import digitalio

import rtc
import time

r = rtc.RTC()
r.datetime = time.struct_time((2024, 4, 5, 7, 0, 0, 0, 0, 1))

while True:
    current_time = r.datetime
    print(current_time)
    time.sleep(5)




rtc=machine.RTC()

file = open("temps.txt", "w")

while True:
    timestamp=rtc.datetime()

    timestring="%04d-%02d-%02d %02d:%02d:%02d"%(timestamp[0:3] +
                                                timestamp[4:7])
    print(timestring)
    utime.sleep(0.01)

    utime.sleep(30)
