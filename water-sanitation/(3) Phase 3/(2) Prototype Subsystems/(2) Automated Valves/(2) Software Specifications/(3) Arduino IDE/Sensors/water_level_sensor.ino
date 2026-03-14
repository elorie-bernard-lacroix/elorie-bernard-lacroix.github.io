// the value of the 'other' resistor
#define SERIESRESISTOR 560    
 
// What pin to connect the sensor to
#define SENSORPIN A0 
 
void setup(void) {
  Serial.begin(9600);
}
 
void loop(void) {
  float reading;
 
  reading = analogRead(SENSORPIN);
 
  Serial.print("Analog reading "); 
  Serial.println(reading);
 
  // convert the value to resistance
  reading = (1023 / reading)  - 1;
  reading = SERIESRESISTOR / reading;
  Serial.print("Sensor resistance "); 
  Serial.println(reading);

  float level;
  if (reading > 2200.0) {
    level = 0.0;
  }
  else{
    // the estimated equation based on eTape data sheet is reading = 2200 - 160 * level
    level = (reading - 2500.0)/-160.0; // adjusted to 2500 since the reading starts from 1500 ohms
  }
  level *= 2.54; // convert inches to cm
  Serial.print("Water level (cm): "); 
  Serial.println(level);
 
  delay(1000);
}