#include <Servo.h>

#define SERVO_PIN 8 // Arduino Nano pin D9 connected to the signal pin of servo motor

Servo servo;  // create servo object to control a servo

int pos = 0;    // variable to store the servo position

void setup() {
  servo.attach(SERVO_PIN);  // attaches the servo on pin 9 to the servo object
}

void loop() {
  for (pos = 0; pos <= 180; pos += 1) { // rotate from 0 degrees to 180 degrees
    // in steps of 1 degree
    servo.write(pos);                   // tell servo to go to position in variable 'pos'
    delay(10);                          // waits 10ms for the servo to reach the position
  }

  for (pos = 180; pos >= 0; pos -= 1) { // rotate from 180 degrees to 0 degrees
    servo.write(pos);                   // tell servo to go to position in variable 'pos'
    delay(10);                          // waits 10ms for the servo to reach the position
  }
}
