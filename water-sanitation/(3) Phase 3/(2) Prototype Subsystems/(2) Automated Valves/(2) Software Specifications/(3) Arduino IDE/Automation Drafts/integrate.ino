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

// LIQUID LEVEL SENSOR
#define SENSORPIN A0 
#define W_SERIESRESISTOR 560

int count = 0;  // count 10 seconds

void setup(void) {
  Serial.begin(9600);
  servo.attach(SERVO_PIN);  // attaches the servo on pin 9 to the servo object
}

void OpenValve() {
  for (pos = 0; pos <= 180; pos += 1) { // rotate from 0 degrees to 180 degrees
    // in steps of 1 degree
    servo.write(pos);                   // tell servo to go to position in variable 'pos'
    delay(10);                          // waits 10ms for the servo to reach the position
  }
}

void CloseValve() {
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

float LiqidLevel() {
  float reading;

  reading = analogRead(SENSORPIN);

  //Serial.print("Analog reading "); 
  //Serial.println(reading);
 
  // convert the value to resistance
  reading = (1023 / reading)  - 1;
  reading = W_SERIESRESISTOR / reading;
  //Serial.print("Sensor resistance "); 
  //Serial.println(reading);

  float level;
  if (reading > 2200.0) {
    level = 0.0;
  }
  else {
    // the estimated equation based on eTape data sheet is reading = 2200 - 160 * level
    level = (reading - 2600.0)/-160.0; // adjusted to 2500 since the reading starts from 1500 ohms
  }
  level *= 2.54; // convert inches to cm

  return level;
}

void loop(void) {
  float temp = Thermistor();
  Serial.print("Temperature: "); 
  Serial.print(temp);
  Serial.println(" *C");

  float water = LiqidLevel();
  Serial.print("Water level: "); 
  Serial.print(water);
  Serial.println(" cm");

  delay(1000);

  if (temp >= 26.0){
    Serial.print("The water has reached over 20*C. Start counting up to 10. \n");
  }

  while ((temp >= 26.0) && (count < 10)) {
    count += 1;
    Serial.print(count);
    Serial.print('\n');
    delay(1000);
    temp = Thermistor();
  }

  delay(1000);

  if (count == 10) {
    Serial.print("The water has reached over 30*C for 10 seconds. \n");
    delay(100);
    Serial.print("Check if there is a space for the water. \n");
    Serial.print('\n');
    water = LiqidLevel();
    if (water <= 20.0) { // CHANGE LATER
      Serial.print("There is a space for the water :) \n");
      delay(100);
      Serial.print("OPEN THE VALUE \n");
      OpenValve();
      Serial.print('\n');
      while (water < 20.0) {
        water = LiqidLevel();
        // just to check; we can remove this later since it prints data a lot
        Serial.print("Water level: "); 
        Serial.print(water);
        Serial.println(" cm \n");
        delay(1000);
      }
      if (water >= 20.0) {
        Serial.print("Water level exceeded 20.0cm \n");
        Serial.print("CLOSE THE VALVE \n");
        CloseValve();
      }
    }
    else {
      Serial.print("There is no space for the water :( \n");
    }
    count = 0;
    delay(1000);
  }

  else {
    count = 0;
  }

  Serial.print('\n');
}