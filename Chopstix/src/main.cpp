#include <Arduino.h>
#include <AccelStepper.h>
#define HALFSTEP 4

// Motors
AccelStepper rotationBase(HALFSTEP, 5, 6, 7, 8);
AccelStepper arm(HALFSTEP, 9, 10, 11, 12);
AccelStepper actuator(HALFSTEP, 1, 3, 2, 4);

// NEMA Motor parameters
const int NEMA_SPEED = 1000;
const int NEMA_ACCEL = 100000;

// Tiny Motor parameters
const int TINY_SPEED = 80;
const int TINY_ACCELERATION = 80;

// Current Coordinates (in steps NOT degrees)
double currBaseLocation;
double currArmInclination;
boolean chopStixOpen;

// Movement Parameters
double TINY_STEPS_TO_CLOSE = 50;
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
  arm.setSpeed(NEMA_SPEED);
  arm.setAcceleration(NEMA_ACCEL);
  actuator.setSpeed(TINY_SPEED);
  actuator.setAcceleration(TINY_ACCELERATION);

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
  if (!(newLocation > MAX_BASE_ROTATION || newLocation < -MAX_BASE_ROTATION))
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
  if (!(newLocation < 0 || newLocation > MAX_ARM_INCLINATION))
  {
    arm.setCurrentPosition(0);
    arm.moveTo(steps);
    while (arm.distanceToGo() != 0)
    {
      arm.run();
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
    baseCommand = command.substring(0, command.length() - 1);
  }
  // get split the command and remove /n from the end
  else
  {
    baseCommand = command.substring(0, space1);
    secondPart = command.substring(space1, command.length() - 1);
  }

  // rb = rotate base
  if (baseCommand.equals("rb"))
  {
    double deg = secondPart.toDouble();
    rotateBaseByDegrees(deg);
  }
  // ra = rotate arm
  if (baseCommand.equals("ra"))
  {
    double deg = secondPart.toDouble();
    rotateArmByDegrees(deg);
  }
  // tc = toggle chopStix
  if (baseCommand.equals("tc"))
  {
    toggleStix();
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

void loop()
{
  // communicationLoop();
  actuator.moveTo(-5000);
  while ((actuator.distanceToGo() != 0))
  {
    actuator.run();
  }
}
