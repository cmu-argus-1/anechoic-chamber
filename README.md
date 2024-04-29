# Anechoic Chamber Setup & Instructions
## Table of Contents
-	Introduction
-	Dependencies
-	Software setup
-	Hardware setup
-	How to use
## Introduction
<img height="320" src="https://github.com/cmu-spacecraft-design-build-fly-2023/anechoic-chamber/assets/75640543/84d44447-41be-4dae-aaec-ef26264e1b58">

This anechoic chamber is used to measure the radiation pattern of the antenna at different angles, which was important for determining nulls on the finished satellite that may differ from the idealized pattern for our dipole antenna due to the chassis, batteries, and other metal-containing parts of the satellite. Here is our low-cost Raspberry Pi-based setup which is ideal for educational purposes.

## Dependencies
### Software
-	Python 3.7+
-	[LibreVNA](https://github.com/jankae/LibreVNA)
-	Numpy
-	Matplotlib
#### Off-the-Shelf Hardware
-	Raspberry Pi 4+
-	[LibreVNA](https://github.com/jankae/LibreVNA)
- Motor setup
  -	[Velmex VXM Stepping Motor Controller](https://www.velmex.com/Products/Controls/VXM_Controller.html)
  -	Motor that can rotate the antenna
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
3.	Edit `.config` with the following options
      - `motor_dut` ID of the motor being stepped. Values are 1, 2, 3, or 4.
      - `vna_path` Path to LibreVNA-GUI
      - `if_bandwidth` Bandwidth in Hz of the intermediate frequency measurement
      - Total number of points being averaged = `pts_1` times `pts_2`:
        - `pts_1` Number of sweeps
        - `pts_2` Number of points per sweep
      - `stim_pwr` Power in dBm sent to the horn antenna
      - `freq` Frequency in Hz of stimulus and measurement
      - `n_angles` Number of angles measured during the single revolution
      - `steps_per_rev` Number of motor steps required to rotate the stage by 360 degrees
      - `init_motor_pos` Motor position in steps of the initialized motor
      - `plot_min` Lower default limit in dB of the plot of the measurements normalized to the maximum value
4.	Run `antenna_pattern.py` to reset the motor to the zero position and ensure that communication with the peripherals can be established.
## Hardware setup
<img width="613" alt="image" src="https://github.com/cmu-spacecraft-design-build-fly-2023/anechoic-chamber/assets/75640543/e1423b4a-d541-428a-9fcd-1e255c3e4a53">

1.	Build a rectangular room using the plywood. Depending on the size of your chamber, ensure that there are doors or trapdoors for easy access to the device under test (port 2) and the horn antenna (port 1).
2.	Cover the walls, floor, and ceiling of the room with the foam absorbers, including the door, but leave a space for the motor and the antenna.
3.	In relation to where the device under test will be placed, set up the motor and PVC pipe directly under that spot, and place the horn antenna on the wall such that it is level with, centered on, and directly faces this spot.
4.	Connect the horn antenna to the vector network analyzer with a coaxial cable.
5.	Connect another coaxial cable to the VNA and attach the other end to the PVC pipe. 
6.	Connect the VNA to the Raspberry Pi through USB.
7.	Connect the motor controller to the Raspberry Pi through USB.
8.	Calibrate the LibreVNA at your desired frequency range by attaching open circuit, short circuit, and 50 ohm dummy loads to port 2. 
## How to use
<img width="433" src="https://github.com/cmu-spacecraft-design-build-fly-2023/anechoic-chamber/assets/75640543/3b25730e-15df-4a29-b81a-0d52f8656855">

1.	Connect the antenna under test to the port 2 coaxial cable and secure it with tape, making note of the antenna’s orientation in relation to the horn antenna.
2.	Edit `.config` for your specific measurement (See step 3 in Software setup)
3.	Close the chamber door and run `antenna_pattern.py`
4.	After the measurement has finished, the plot and raw measurements will be stored in the same directory as `antenna_pattern.py`. 
