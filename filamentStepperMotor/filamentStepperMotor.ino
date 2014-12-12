//  Demo function:The application method to drive the stepper motor.
//  Hareware:Stepper motor - 24BYJ48,Seeed's Motor Shield v2.0
//  Author:Frankie.Chu
//  Date:20 November, 2012
#include <stdlib.h>
#include <math.h>
#define MOTOR_CLOCKWISE      0
#define MOTOR_ANTICLOCKWISE  1
/******Pins definitions*************/
#define MOTORSHIELD_IN1	8
#define MOTORSHIELD_IN2	11
#define MOTORSHIELD_IN3	12
#define MOTORSHIELD_IN4	13
#define CTRLPIN_A		9
#define CTRLPIN_B		10

const unsigned char stepper_ctrl[]={0x27,0x36,0x1e,0x0f};
struct MotorStruct
{
	int8_t speed;
	uint8_t direction;
};
MotorStruct stepperMotor;
unsigned int number_of_steps = 50;
float steps_per_millimeter = 1.5;
int offset = 25;
/**********************************************************************/
/*Function: Get the stepper motor rotate                               */
/*Parameter:-int steps,the total steps and the direction the motor rotates.*/
/*			if steps > 0,rotates anticlockwise,			   			   */
/*			if steps < 0,rotates clockwise.           				   */
/*Return:	void                      							      */
void step(int steps)
{
        // Flip so that input steps are clockwise
        steps = -steps;
	int steps_left = abs(steps)*4;
	int step_number;
	int millis_delay = 60L * 1000L / number_of_steps / (stepperMotor.speed + 50);
	if (steps > 0) 
	{
		stepperMotor.direction= MOTOR_ANTICLOCKWISE;
		step_number = 0; 
	}
    else if (steps < 0) 
	{
		stepperMotor.direction= MOTOR_CLOCKWISE;
		step_number = number_of_steps;
	}
	else return;
	while(steps_left > 0) 
	{
		PORTB = stepper_ctrl[step_number%4];
		delay(millis_delay);
		if(stepperMotor.direction== MOTOR_ANTICLOCKWISE)
		{
		    step_number++;
		    if (step_number == number_of_steps)
		    	step_number = 0;
		}
		else 
		{
		    step_number--;
		    if (step_number == 0)
		    	step_number = number_of_steps;
		}
		steps_left--;
		
	}
}
void initialize()
{
	pinMode(MOTORSHIELD_IN1,OUTPUT);
	pinMode(MOTORSHIELD_IN2,OUTPUT);
	pinMode(MOTORSHIELD_IN3,OUTPUT);
	pinMode(MOTORSHIELD_IN4,OUTPUT);
	pinMode(CTRLPIN_A,OUTPUT);
	pinMode(CTRLPIN_B,OUTPUT);
	stop();
//        stepperMotor.speed = 25;
	stepperMotor.speed = 20;
	stepperMotor.direction = MOTOR_CLOCKWISE;
}
/*******************************************/
void stop()
{
    /* Unenble the pin, to stop the motor. */
    digitalWrite(CTRLPIN_A,LOW);
    digitalWrite(CTRLPIN_B,LOW);
}

void setup()
{
   Serial.begin(115200);
   initialize();//Initialization for the stepper motor.
   
}

void stepCalculator(float input){
  step((int)floor(input * steps_per_millimeter));
}

char current;
char *buf = (char *)malloc(sizeof(char) * 50);
unsigned int i = 0;

void loop()
{
  int switched = digitalRead(2);
  // Read loop
  if (switched) {
    if (Serial.available() > 0){
      current = Serial.read();         
      if (current == '\n'){
        buf[i] = '\0';
        // Parse the buffered string
        char command = buf[0];
        switch(command){
         case 'E':
         {
           float amount = atof(buf + 1);
           Serial.println(amount);
           // Dispatch to the stepper
           stepCalculator(amount);
           break;
           
         }
         case 'S':{
           stepCalculator(-offset);
         }
        }
        i = 0;
        return;
      }
      buf[i] = current;
      i++; 
    }
  }
  else{
   step(50);
   delay(5000);
   
  }
}
