# Anechoic Chamber Setup & Instructions
## Table of Contents
-	Introduction
-	Dependencies
-	Software setup
-	Hardware setup
-	How to use
## Introduction
The anechoic chamber is used to measure the radiation pattern of the antenna at different angles, which was important for determining nulls on the finished satellite that differ from the idealized pattern for our dipole antenna. Here is our low-cost Raspberry Pi-based setup which is ideal for educational purposes.
## Dependencies
### Software
-	Python 3.7+
-	LibreVNA
-	Numpy
-	Matplotlib
#### Off-the-Shelf Hardware
-	Raspberry Pi 4+
-	LibreVNA
-	Velmex VXM Motor Controller and motors
  -	RS-232 to USB-A cable
### Other Hardware
-	Foam absorbers
-	Room
  -	Wood, plywood
  -	Door, trapdoor
-	Coaxial cables with SMA connectors
-	Open circuit, short circuit, and 50 ohm loads for calibration
-	Horn antenna
-	Mount for device under test
  -	PVC pipe
  -	Additional supports such as plastic boards and tape
## Software setup
1.	This chamber is controlled by a Raspberry Pi 4 with the listed dependencies installed because it has at least 2 USB ports to connect to the VNA and the motor controller, it can run Linux (We used Raspbian OS 12), and (optional) it can connect to the Internet for remote access.
2.	Clone this repo
3.	Run antenna_pattern.py to reset the motor to the zero position and make sure that communication with the peripherals can be established.
## Hardware setup
1.	Build a rectangular room using the plywood. Depending on the size of your chamber, ensure that there are doors or trapdoors for easy access to the device under test (port 2) and the horn antenna (port 1).
2.	Cover the walls, floor, and ceiling of the room with the foam absorbers, including the door, but leave a space for the motor and the antenna.
3.	In relation to where the device under test will be placed, set up the motor and PVC pipe directly under that spot, and place the horn antenna on the wall such that it is level with, centered on, and directly faces this spot.
4.	Connect the horn antenna to the vector network analyzer with a coaxial cable.
5.	Connect another coaxial cable to the VNA and attach the other end to the PVC pipe. 
6.	Connect the VNA to the Raspberry Pi through USB.
7.	Connect the motor controller to the Raspberry Pi through USB.
8.	Calibrate the LibreVNA at your desired frequency range by attaching open circuit, short circuit, and 50 ohm dummy loads to port 2. 
## How to use
1.	Connect the antenna under test to the port 2 coaxial cable and secure it with tape, making note of the antenna’s orientation in relation to the horn antenna.
2.	Close the chamber door and run antenna_pattern.py after changing following options:
a.	Frequency range
b.	Angle range
c.	Number of points to average over
d.	Output: plot, csv
3.	After the measurement has been completed, the radiation pattern can be viewed.
