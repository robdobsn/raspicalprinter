# Calendar Printer
# Rob Dobson 2013
# Adapted from Adafruit pi-thermal-printer project

from __future__ import print_function
import RPi.GPIO as GPIO
from Adafruit_Thermal import *
import time, socket
from calendars import Calendars
import os

ledPin = 18
buttonPins = [ 24, 23, 22, 25 ]
powerSensePin = 17
batteryPowerOnPin = 27

calendars = Calendars()

printer = Adafruit_Thermal("/dev/ttyAMA0", 19200, timeout=5)

# Use Broadcom pin numbers (not Raspberry Pi pin numbers) for GPIO
GPIO.setmode(GPIO.BCM)

# Enable battery power and sense
GPIO.setup(batteryPowerOnPin, GPIO.OUT)
GPIO.output(batteryPowerOnPin, GPIO.HIGH)
GPIO.setup(powerSensePin, GPIO.IN)

# Enable LED and button (w/pull-up on latter)
GPIO.setup(ledPin, GPIO.OUT)
for buttonPin in buttonPins:
    GPIO.setup(buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# LED on for now
GPIO.output(ledPin, GPIO.HIGH)

# Processor load is heavy at startup; wait a moment to avoid
# stalling during greeting.
time.sleep(30)

printer.feed(2)
printer.boldOn()
printer.print("Grace & Dad's Calendar Printer")
printer.boldOff()
printer.feed(1)

# Show IP address (if network is available)
try:
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(('8.8.8.8', 0))
	printer.print('My IP address is ' + s.getsockname()[0])
	printer.feed(3)
except:
	printer.boldOn()
	printer.println('Network is unreachable.')
	printer.boldOff()
	printer.print('Connect display and keyboard\n'
	  'for network troubleshooting.')
	printer.feed(3)
	exit(0)

# Poll initial button state and time
prevButtonStates = []
prevTimes = []
for buttonPin in buttonPins:
    prevButtonStates.append(GPIO.input(buttonPin))
    prevTimes.append(time.time())

# Main loop
exitProgram = False
while(not exitProgram):

    t = time.time()
    for i in range(len(buttonPins)):
        # Poll current button state and time
        buttonState = GPIO.input(buttonPins[i])

        # Has button state changed?
        if buttonState != prevButtonStates[i]:
            prevButtonStates[i] = buttonState   # Yes, save new state/time
            prevTimes[i] = t
            #print ("Button " + str(i) + " = " + str(buttonState))
            if buttonState == True:
                if i == 0:
                    calendars.printCal(printer, "")
                    printer.feed(3)
                elif i == 1:
                    calendars.printCal(printer, "Grace")
                    printer.feed(3)
                elif i == 2:
                    calendars.printCal(printer, "Joe")
                    printer.feed(3)
                elif i == 3:
                    printer.print('My IP address is ' + s.getsockname()[0])
                    printer.feed(3)

        # Check for a button held down for x seconds
        elif buttonState == False and time.time() > prevTimes[i] + 5:
            if i == 3:
                printer.print("Shutting down ...")
                printer.feed(3)
                time.sleep(5)
                os.system("sudo shutdown -h now")
                exitProgram = True
                break
            elif i == 2:
                printer.print("Exiting calendar printer")
                printer.feed(3)
                time.sleep(5)
                exitProgram = True
                break
            
    # Check power sense to see if shutdown is required
    powerSense = GPIO.input(powerSensePin)
    if powerSense == False:
        os.system("sudo shutdown -h now")
        break
    
    # LED blinks while idle, for a brief interval every 2 seconds.
    # Pin 18 is PWM-capable and a "sleep throb" would be nice, but
    # the PWM-related library is a hassle for average users to install
    # right now.  Might return to this later when it's more accessible.
    if ((int(t) & 1) == 0) and ((t - int(t)) < 0.15):
        GPIO.output(ledPin, GPIO.HIGH)
    else:
        GPIO.output(ledPin, GPIO.LOW)

