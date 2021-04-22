#include <AccelStepper.h>
#include <Servo.h>

// defines pins numbers
const int enPinX = 2;
const int stepPinX = 3; 
const int dirPinX = 4;
const int ms1PinX = 5;
const int ms2PinX = 6;

const int enPinY = 8;
const int stepPinY = 9; 
const int dirPinY = 10;
const int ms1PinY = 11;
const int ms2PinY = 12;

const int irLightPin = 13;

const int tiggerServoPin = 7;

const int limitSwitchXPin = A0;
const int limitSwitchYPin = A1;

unsigned int desPosX, desPosY, triggerPos, stepperSpeed, stepperAcceleration = 0;
unsigned int maxX = 5000;
unsigned int maxY = 2000;


AccelStepper stepperX;
AccelStepper stepperY;

Servo triggerServo;
 
void setup() {
  triggerServo.attach(tiggerServoPin);
  pinMode(enPinX, OUTPUT);
  pinMode(enPinY, OUTPUT);
  pinMode(ms1PinX, OUTPUT);
  pinMode(ms1PinY, OUTPUT);
  pinMode(ms2PinX, OUTPUT);
  pinMode(ms2PinY, OUTPUT);
  pinMode(irLightPin, OUTPUT);
  pinMode(limitSwitchXPin, INPUT_PULLUP);
  pinMode(limitSwitchYPin, INPUT_PULLUP);

  digitalWrite(enPinX, HIGH); // Disable stepper on X
  digitalWrite(enPinY, HIGH); // Disable stepper on Y
  
  digitalWrite(ms1PinX, HIGH); // Set 1⁄16 step on X 
  digitalWrite(ms2PinX, HIGH);
  
  digitalWrite(ms1PinY, HIGH); // Set 1⁄16 step on X
  digitalWrite(ms2PinY, HIGH);

  Serial.begin(115200);

  stepperX = AccelStepper(AccelStepper::DRIVER, stepPinX, dirPinX, NULL, NULL);
  stepperX.setMaxSpeed(2500);
  stepperX.setAcceleration(4000);
  
  stepperY = AccelStepper(AccelStepper::DRIVER, stepPinY, dirPinY, NULL, NULL);
  stepperY.setMaxSpeed(2500);
  stepperY.setAcceleration(4000);
}

const byte numChars = 32;

// https://stackoverflow.com/questions/9072320/split-string-into-string-array
String getValue(String data, char separator, int index)
{
  int found = 0;
  int strIndex[] = {0, -1};
  int maxIndex = data.length()-1;

  for(int i=0; i<=maxIndex && found<=index; i++){
    if(data.charAt(i)==separator || i==maxIndex){
        found++;
        strIndex[0] = strIndex[1]+1;
        strIndex[1] = (i == maxIndex) ? i+1 : i;
    }
  }

  return found>index ? data.substring(strIndex[0], strIndex[1]) : "";
}

void recvWithEndMarker() {
    static byte ndx = 0;
    char endMarker = '\n';
    char rc;
    static char command = 'u';
    static char receivedChars[numChars];
   
    while (Serial.available() > 0) {
        rc = Serial.read();
        
        if (ndx == 0)
        {
          command = rc;
          ndx++;
          continue;
        }
        
        if (rc != endMarker) {
            receivedChars[ndx-1] = rc;
            ndx++;
            if (ndx >= numChars) {
                ndx = numChars - 1;
            }
        }
        else {
            receivedChars[ndx-1] = '\0';
            int value = atoi(receivedChars);
            if (command == 'x')
            {
              desPosX = value;
            }
            if (command == 'y')
            {
              desPosY = value;
            }
            if (command == 'e')
            {
              if (value == 1)
              {
                  digitalWrite(enPinX, LOW); // Enable stepper on X
                  digitalWrite(enPinY, LOW); // Enable stepper on Y
              }
              else
              {
                  digitalWrite(enPinX, HIGH); // Disable stepper on X
                  digitalWrite(enPinY, HIGH); // Disable stepper on Y
              }
            }
            if (command == 'a')
            {
              stepperAcceleration = value;
              stepperX.setAcceleration(stepperAcceleration);
              stepperY.setAcceleration(stepperAcceleration);
            }
            if (command == 's')
            {
              stepperSpeed = value;
              stepperX.setMaxSpeed(stepperSpeed);
              stepperY.setMaxSpeed(stepperSpeed);
            }

            if (command == 't')
            {
              triggerPos = value;
            }

            if (command == 'l')
            {
              if (value == 1)
              {
                digitalWrite(irLightPin, HIGH); // turn on light
              }
              else
              {
                digitalWrite(irLightPin, LOW); // turn off light
              }
            }

            if (command == 'r')
            {
              resetPosition();
            }
            ndx = 0;
            command = 'u';
        }
    }
}


void zeroStepper(AccelStepper stepper, int limitSwitchPin)
{
  // set slow speed for stepper
  stepper.setMaxSpeed(150);
  stepper.setAcceleration(100);

  // run backward until limit switch is triggered
  stepper.moveTo(-10000);
  while (digitalRead(limitSwitchPin) == HIGH)
    stepper.run();
  stepper.stop();
  
  // set position to zero.
  stepper.setCurrentPosition(0);

  // reset stepper speed for stepper x
  stepper.setMaxSpeed(stepperSpeed);
  stepper.setAcceleration(stepperAcceleration);
}

void resetPosition()
{
  // zero stepper x
  zeroStepper(stepperX, limitSwitchXPin);

  // zero stepper y
  zeroStepper(stepperY, limitSwitchYPin);
  
  // move to center
  stepperX.moveTo(maxX/2);
  stepperY.moveTo(maxY/2);
}

void loop() {
  recvWithEndMarker();
  
  stepperX.moveTo(desPosX);
  stepperX.run();

  stepperY.moveTo(desPosY);
  stepperY.run();
  
  triggerServo.write(triggerPos);
}
