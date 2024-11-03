import serial
import time

# the port computer sees arduino at
COM_PORT = "\\\\.\\COM7"

serialRead = serial.Serial(
    port=COM_PORT, baudrate=9600, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE
)


# encodes to write to sepytrial
def serialWrite(inp):
    time.sleep(0.1)
    serialRead.write(str.encode(inp))


# tell arduino to rotate base given number of degrees
def rotateBase(deg):
    serialWrite("rb " + str(deg))


# tell arduino to rotate arm given number of degrees
def rotateArm(deg):
    serialWrite("ra " + str(deg))


# tell arduino to toggle chopstix
def toggleSticks():
    serialWrite("tc")


# zero out the axis'
def zeroAxis():
    serialWrite("z")
