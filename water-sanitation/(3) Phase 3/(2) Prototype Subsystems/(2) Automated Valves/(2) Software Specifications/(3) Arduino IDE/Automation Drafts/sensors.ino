// THERMISTOR
#define THERMISTORPIN A1        
#define T_SERIESRESISTOR 10000
// resistance at 25 degrees C
#define THERMISTORNOMINAL 10000      
// temp. for nominal resistance (almost always 25 C)
#define TEMPERATURENOMINAL 25   
// The beta coefficient of the thermistor (usually 3000-4000)
#define BCOEFFICIENT 3950

// WATER LEVEL SENSOR
#define SENSORPIN A0 
#define W_SERIESRESISTOR 560    
 
void setup(void) {
  Serial.begin(9600);
}
 
void loop(void) {
  // THERMISTOR
  float t_reading;
 
  t_reading = analogRead(THERMISTORPIN);
 
  //Serial.print("Analog reading "); 
  //Serial.println(t_reading);
 
  // convert the value to resistance
  t_reading = (1023 / t_reading)  - 1;     // (1023/ADC - 1) 
  t_reading = T_SERIESRESISTOR / t_reading;  // 10K / (1023/ADC - 1)
  //Serial.print("Thermistor resistance "); 
  //Serial.println(t_reading);

  float steinhart;
  steinhart = t_reading / THERMISTORNOMINAL;     // (R/Ro)
  steinhart = log(steinhart);                  // ln(R/Ro)
  steinhart /= BCOEFFICIENT;                   // 1/B * ln(R/Ro)
  steinhart += 1.0 / (TEMPERATURENOMINAL + 273.15); // + (1/To)
  steinhart = 1.0 / steinhart;                 // Invert
  steinhart -= 273.15;                         // convert absolute temp to C
  
  Serial.print("Temperature: "); 
  Serial.print(steinhart);
  Serial.println(" *C");

  // WATER LEVEL SENSOR
  float w_reading;
 
  w_reading = analogRead(SENSORPIN);
 
  //Serial.print("Analog reading "); 
  //Serial.println(w_reading);
 
  // convert the value to resistance
  w_reading = (1023 / w_reading)  - 1;
  w_reading = W_SERIESRESISTOR / w_reading;
  //Serial.print("Sensor resistance "); 
  //Serial.println(w_reading);

  float level;
  if (w_reading > 2200.0) {
    level = 0.0;
  }
  else{
    // the estimated equation based on eTape data sheet is reading = 2200 - 160 * level
    level = (w_reading - 2500.0)/-160.0; // adjusted to 2500 since the reading starts from 1500 ohms
  }
  level *= 2.54; // convert inches to cm
  Serial.print("Water level: "); 
  Serial.print(level);
  Serial.println(" cm");
 
  delay(1000);
}