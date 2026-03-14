// Boiling to Hot
// 1. Check if the water in the boiling tank is boiled enough.
//  a. If the water is boiled enough, move to step 2.
//  b. If the water is not boiled enough, keep looping.
// 2. Count up to 10 seconds.
//  a. If the water gets cold while counting, the counting stops.
//  b. If the water’s temperature maintained for 10 seconds, move to step 3.
// For prototyping, do not add extra boiling water while the system's hot water tank is not emptied.
// 3. Open the valve.
// 4. Close the valve.

// SERVO MOTOR
#include <Servo.h>
#define SERVO_PIN 8 // Arduino Nano pin D9 connected to the signal pin of servo motor
Servo servo;  // create servo object to control a servo
int pos = 0;    // variable to store the servo position

// THERMISTOR
#define THERMISTORPIN A1        
#define T_SERIESRESISTOR 10000
// resistance at 25 degrees C
#define THERMISTORNOMINAL 10000      
// temp. for nominal resistance (almost always 25 C)
#define TEMPERATURENOMINAL 25   
// The beta coefficient of the thermistor (usually 3000-4000)
#define BCOEFFICIENT 3950

int count = 0;  // count 10 seconds

void setup(void) {
  Serial.begin(9600);
  servo.attach(SERVO_PIN);  // attaches the servo on pin 9 to the servo object
  OpenValve();
}

void CloseValve() {
  for (pos = 0; pos <= 180; pos += 1) { // rotate from 0 degrees to 180 degrees
    // in steps of 1 degree
    servo.write(pos);                   // tell servo to go to position in variable 'pos'
    delay(10);                          // waits 10ms for the servo to reach the position
  }
}

void OpenValve() {
  for (pos = 180; pos >= 0; pos -= 1) { // rotate from 180 degrees to 0 degrees
      servo.write(pos);                   // tell servo to go to position in variable 'pos'
      delay(10);                          // waits 10ms for the servo to reach the position
    }
}

float Thermistor() {
  float reading;

  reading = analogRead(THERMISTORPIN);

  //Serial.print("Analog reading "); 
  //Serial.println(t_reading);
 
  // convert the value to resistance
  reading = (1023 / reading)  - 1;     // (1023/ADC - 1) 
  reading = T_SERIESRESISTOR / reading;  // 10K / (1023/ADC - 1)
  //Serial.print("Thermistor resistance "); 
  //Serial.println(reading);

  float steinhart;
  steinhart = reading / THERMISTORNOMINAL;     // (R/Ro)
  steinhart = log(steinhart);                  // ln(R/Ro)
  steinhart /= BCOEFFICIENT;                   // 1/B * ln(R/Ro)
  steinhart += 1.0 / (TEMPERATURENOMINAL + 273.15); // + (1/To)
  steinhart = 1.0 / steinhart;                 // Invert
  steinhart -= 273.15;                         // convert absolute temp to C

  return steinhart;
}

void loop(void) {
  float temp = Thermistor();
  Serial.print("Temperature in the boiling water tank: "); 
  Serial.print(temp);
  Serial.println(" *C");

  delay(1000);

  if (temp >= 29.0){
    Serial.print("The water has reached over 26*C. Start counting up to 10. \n");
  }

  while ((temp >= 29.0) && (count < 10)) {
    count += 1;
    Serial.print(count);
    Serial.print('\n');
    delay(1000);
    temp = Thermistor();
  }

  if (count == 10) {
    Serial.print("The water has reached over 30*C for 10 seconds. \n");
    delay(100);
    Serial.print("OPEN THE VALUE \n");
    OpenValve();
    delay(1000); // depend on the flow rate
    Serial.print("25% dispensed \n");
    delay(1000); // depend on the flow rate
    Serial.print("50% dispensed \n");
    delay(1000); // depend on the flow rate
    Serial.print("75% dispensed \n");
    delay(1000); // depend on the flow rate
    Serial.print("100% dispensed \n");
    Serial.print("CLOSE THE VALVE \n");
    CloseValve();
    count = 0;
  }

  else {
    count = 0;
  }

  Serial.print('\n');
}