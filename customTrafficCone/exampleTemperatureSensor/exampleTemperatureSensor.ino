
/*
 * Inputs ADC Value from Thermistor and outputs Temperature in Celsius
 *  requires: include <math.h>
 * Utilizes the Steinhart-Hart Thermistor Equation:
 *    Temperature in Kelvin = 1 / {A + B[ln(R)] + C[ln(R)]3}
 *    where A = 0.001129148, B = 0.000234125 and C = 8.76741E-08
 *
 * These coefficients seem to work fairly universally, which is a bit of a 
 * surprise. 
 *
 * Schematic:
 *   [Ground] -- [10k-pad-resistor] -- | -- [thermistor] --[Vcc (5 or 3.3v)]
 *                                               |
 *                                          Analog Pin 0
 *
 * In case it isn't obvious (as it wasn't to me until I thought about it), the analog ports
 * measure the voltage between 0v -> Vcc which for an Arduino is a nominal 5v, but for (say) 
 * a JeeNode, is a nominal 3.3v.
 *
 * The resistance calculation uses the ratio of the two resistors, so the voltage
 * specified above is really only required for the debugging that is commented out below
 *
 * Resistance = PadResistor * (1024/ADC -1)  
 *
 * I have used this successfully with some CH Pipe Sensors (http://www.atcsemitec.co.uk/pdfdocs/ch.pdf)
 * which be obtained from http://www.rapidonline.co.uk.
 *
 */

#include <math.h>

#define ThermistorPIN 0                 // Analog Pin 0
// Steinhart-Hart Equation coefficients, generate using the following data
//53000 Ohms = 23C
//43500 Ohms = 27C
//37500 Ohms = 30C
//12000 Ohms = 100C
//733   Ohms = 200C
//1250  Ohms = 149C
// New ABC
//#define A 0.003759325431
//#define B 0.0010779671
//#define C -0.000004314127533
// Old ABC
#define A 0.002177290523
#define B 0.00004984386308
#define C 0.0000005105364710

#include <PID_v1.h>
#define RelayPin 5

// PID Stuff
//Define Variables we'll be connecting to
double Setpoint, Input, Output;

//Specify the links and initial tuning parameters
PID myPID(&Input, &Output, &Setpoint, 2, 5, 4, DIRECT);

int WindowSize = 5000;
unsigned long windowStartTime;

// Thermistor stuff

float vcc = 4.91;                       // only used for display purposes, if used
                                        // set to the measured Vcc.
float pad = 9850;                       // balance/pad resistor value, set this to
                                        // the measured resistance of your pad resistor
float thermr = 10000;                   // thermistor nominal resistance

float Thermistor(int RawADC) {
  long Resistance;  
  float Temp;  // Dual-Purpose variable to save space.

  Resistance=pad*((1024.0 / RawADC) - 1); 
  Temp = log(Resistance); // Saving the Log(resistance) so not to calculate  it 4 times later
  Temp = 1 / (A + (B * Temp) + (C * Temp * Temp * Temp));
  Temp = Temp - 273.15;  // Convert Kelvin to Celsius                      

  // BEGIN- Remove these lines for the function not to display anything
  //Serial.print("ADC: "); 
  //Serial.print(RawADC); 
  //Serial.print("/1024");                           // Print out RAW ADC Number
  //Serial.print(", vcc: ");
  //Serial.print(vcc,2);
  //Serial.print(", pad: ");
  //Serial.print(pad/1000,3);
  //Serial.print(" Kohms, Volts: "); 
  //Serial.print(((RawADC*vcc)/1024.0),3);   
  //Serial.print(", Resistance: "); 
  //Serial.print(Resistance);
  //Serial.print(" ohms, ");
  // END- Remove these lines for the function not to display anything

  // Uncomment this line for the function to return Fahrenheit instead.
  //temp = (Temp * 9.0)/ 5.0 + 32.0;                  // Convert to Fahrenheit
  return Temp;                                      // Return the Temperature
}

int MotorControl = 5;

void setup() {
  Serial.begin(115200);
  // HeaterControl
  pinMode(MotorControl, OUTPUT);
  
  // PID Controller
  windowStartTime = millis();

  // Temperature to aim PID controller at
  Setpoint = 65.0;

  //tell the PID to range between 0 and the full window size
  myPID.SetOutputLimits(0, WindowSize);

  //turn the PID on
  myPID.SetMode(AUTOMATIC);
}

long previousMillis = 0;
long interval = 200;

void loop() {
  double temp;
  temp=Thermistor(analogRead(ThermistorPIN));       // read ADC and  convert it to Celsius
  int heater_on = digitalRead(2);
  
  // Print on an interval
  unsigned long now = millis();
  if(now - previousMillis > interval) {
    // save the last time you blinked the LED 
    previousMillis = now;   

    Serial.print("Celsius: "); 
    Serial.print(temp,1);                             // display Celsius
    //temp = (temp * 9.0)/ 5.0 + 32.0;                  // converts to  Fahrenheit
    //Serial.print(", Fahrenheit: "); 
    //Serial.print(temp,1);                             // display  Fahrenheit
    Serial.println("");
    
    Serial.print(digitalRead(2));
    Serial.print("\n");
  }

  /************************************************
   * turn the output pin on/off based on pid output
   ************************************************/
  
  if(heater_on){
    myPID.SetMode(AUTOMATIC);
    Input = temp;
    myPID.Compute();
  
    if(now - windowStartTime>WindowSize)
    { //time to shift the Relay Window
      windowStartTime += WindowSize;
    }
    if(Output > now - windowStartTime) digitalWrite(RelayPin,HIGH);
    else digitalWrite(RelayPin,LOW);  
  }
 else{
    myPID.SetMode(MANUAL);
    if(now - windowStartTime>WindowSize)
    { //time to shift the Relay Window
      windowStartTime += WindowSize;
    }
    digitalWrite(MotorControl, LOW); 
 }

//  delay(100);                                      // Delay a bit...  
}

/********************************************************
 * PID RelayOutput Example
 * Same as basic example, except that this time, the output
 * is going to a digital pin which (we presume) is controlling
 * a relay.  The pid is designed to output an analog value,
 * but the relay can only be On/Off.
 *
 *   To connect them together we use "time proportioning
 * control"  Tt's essentially a really slow version of PWM.
 * First we decide on a window size (5000mS say.) We then 
 * set the pid to adjust its output between 0 and that window
 * size.  Lastly, we add some logic that translates the PID
 * output into "Relay On Time" with the remainder of the 
 * window being "Relay Off Time"
 ********************************************************/
