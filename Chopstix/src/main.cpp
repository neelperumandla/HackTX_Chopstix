#include <Arduino.h>
#include <AccelStepper.h>
#define HALFSTEP 4
#define MotorInterfaceType 4

// Motors
AccelStepper rotationBase(HALFSTEP, 5, 6, 7, 8);
AccelStepper arm1(HALFSTEP, 9, 10, 11, 12);
AccelStepper arm2(HALFSTEP, A2, A3, A4, A5);
AccelStepper actuator(MotorInterfaceType, 13, 3, 2, 4);

// NEMA Motor parameters
const int NEMA_SPEED = 1000;
const int NEMA_ACCEL = 10000;

// Tiny Motor parameters
const int TINY_SPEED = 80;
const int TINY_ACCELERATION = 80;

// Current Coordinates (in steps NOT degrees)
double currBaseLocation;
double currArmInclination;
boolean chopStixOpen;

// Movement Parameters
double TINY_STEPS_TO_CLOSE = 200;
double BASE_STEPS_PER_DEGREE = (200.0 / 360.0) * (35.0 / 83.0);
double AMR_STEPS_PER_DEGREES = 200.0 / 360.0;
double MAX_BASE_ROTATION = 90;   // base can rotate 90 deg either direction
double MAX_ARM_INCLINATION = 90; // can rotate up 90 degrees

// used to tell communication computer something bad happened
void sendError(String error)
{
  Serial.println("ERROR" + error);
}

// Set all zeros
// Move all axis to zero position prior to running
void zeroAxis()
{
  currBaseLocation = 0;
  currArmInclination = 0;
  chopStixOpen = true;
}

void setup()
{
  // setup motors
  rotationBase.setMaxSpeed(NEMA_SPEED);
  rotationBase.setAcceleration(NEMA_ACCEL);
  arm1.setMaxSpeed(NEMA_SPEED);
  arm1.setAcceleration(NEMA_ACCEL);
  arm2.setMaxSpeed(NEMA_SPEED);
  arm2.setAcceleration(NEMA_ACCEL);
  actuator.setMaxSpeed(TINY_SPEED);
  actuator.setAcceleration(TINY_ACCELERATION);
  actuator.setMaxSpeed(TINY_SPEED);

  // serial setup
  Serial.begin(9600);

  // Assume the arm was in zero position prior to starting
  zeroAxis();
}

// rotates to new base position by steps
void rotateBaseBySteps(int steps)
{
  int newLocation = currBaseLocation + steps;

  // make sure not out of bounds
  if (true)
  {
    rotationBase.setCurrentPosition(0);
    rotationBase.moveTo(steps);
    while (rotationBase.distanceToGo() != 0)
    {
      rotationBase.run();
    }
    currBaseLocation = newLocation;
  }
  else
  {
    sendError("base rotation out of bounds");
  }
}

// rotates inclination by degrees
void rotateArmBySteps(int steps)
{
  int newLocation = currArmInclination + steps;

  // make sure not out of bounds
  if (true)
  {
    arm1.setCurrentPosition(0);
    arm2.setCurrentPosition(0);
    arm1.moveTo(steps);
    arm2.moveTo(steps);
    while (arm1.distanceToGo() != 0)
    {
      arm1.run();
      arm2.run();
    }
    currArmInclination = newLocation;
  }
  else
  {
    sendError("rotate arm out of bounds");
  }
}

// rotates base position by degrees
void rotateBaseByDegrees(double deg)
{
  rotateBaseBySteps(int(deg * BASE_STEPS_PER_DEGREE));
}

// rotates arm by degrees
void rotateArmByDegrees(double deg)
{
  rotateArmByDegrees(int(deg * AMR_STEPS_PER_DEGREES));
}

// open or close the chopsticks from their current position
void toggleStix()
{
  actuator.setCurrentPosition(0);
  if (chopStixOpen)
  {
    actuator.moveTo(TINY_STEPS_TO_CLOSE);
  }
  else
  {
    actuator.moveTo(-TINY_STEPS_TO_CLOSE);
  }
  while (actuator.distanceToGo() != 0)
  {
    actuator.run();
  }
  chopStixOpen = !chopStixOpen;
}

// return base location in degrees
double getBaseLocation()
{
  return currBaseLocation * BASE_STEPS_PER_DEGREE;
}

// return arm location in degrees
double getArmLocation()
{
  return currArmInclination * AMR_STEPS_PER_DEGREES;
}

// return if the chopsticks are open
boolean isChopstixOpen()
{
  return chopStixOpen;
}

// used to communicate over serial
void communicationLoop()
{
  // the base command
  String command = Serial.readString();
  int space1 = command.indexOf(" ");
  String baseCommand;
  String secondPart;

  // remove /n from command
  if (space1 == -1)
  {
    baseCommand = command.substring(0, command.length());
  }
  // get split the command and remove /n from the end
  else
  {
    baseCommand = command.substring(0, space1);
    secondPart = command.substring(space1 + 1, command.length());
  }

  // rb = rotate base
  if (baseCommand.equals("rb"))
  {
    int steps = secondPart.toInt();
    rotateBaseBySteps(steps);
  }
  // ra = rotate arm
  if (baseCommand.equals("ra"))
  {
    int steps = secondPart.toInt();
    rotateArmBySteps(steps);
    Serial.println("running arms " + String(steps));
  }
  // tc = toggle chopStix
  if (baseCommand.equals("tc"))
  {
    toggleStix();
    Serial.println("running already");
  }
  // z = zeroAxis
  if (baseCommand.equals("z"))
  {
    zeroAxis();
  }
  // gc = get chopstix open
  if (baseCommand.equals("gc"))
  {
    if (isChopstixOpen())
    {
      Serial.println("TRUE");
    }
    else
    {
      Serial.println("FALSE");
    }
  }
  else
  {
    sendError("unknown command");
  }
}
boolean done = true;
void loop()
{

  if (done)
  {
    // toggleStix();
    done = false;
  }
  communicationLoop();
}
