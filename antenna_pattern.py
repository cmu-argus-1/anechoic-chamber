
#!/usr/bin/env python3
import time
import serial
import re
import numpy as np
import subprocess
import matplotlib.pyplot as plt
from libreVNA import libreVNA

MOTOR_DUT = 1
POS_CHECK = ["", "X", "Y", "Z", "T"]
VNA_PATH = "/Desktop/LibreVNA-GUI"

# Sweep settings
n_freqs = 3
freq_min = 915e6 - 20000
freq_max = 915e6 + 20000
out_power = -10
if_bandwidth = 100
avg_pts = 128

# Motor settings
n_angles = 360
steps_per_rev = 14400
init_motor_positions = [0]

# Check that motor is ready to receive commands
def motor_ready(conn):
    conn.write("V".encode(encoding="ascii"))
    response = conn.readline().decode("ascii")
    if response == "R":
        return True
    elif response == "B":
        # Kill processes if busy and check once again
        conn.write("K".encode(encoding="ascii"))
        response = conn.readline().decode("ascii")
        if response == "R":
            return True
        else:
            return False
    else:
        return False

# Move motor to specified position
def move_motor(conn, motor_id, pos):
    pos = int(pos)
    letter = POS_CHECK[motor_id]
    conn.write(letter.encode(encoding="ascii"))
    read = conn.readline().decode("ascii")
    current_pos = int(re.findall(r"[+-]\d+", read)[0])
    next_pos = current_pos - current_pos % steps_per_rev + pos % steps_per_rev
    command = f"C E IA{motor_id}M{next_pos},R"
    conn.write(command.encode(encoding="ascii"))
    conn.readline()
    
    while(current_pos % steps_per_rev != pos):
        time.sleep(0.1)
        conn.write(letter.encode(encoding="ascii"))
        read = conn.readline().decode("ascii")
        current_pos = int(re.findall("[+-]\d+", read)[0])
    return True

# Set all motors to initial positions
def init_motors(conn, pos_list):
    for index, init_pos in enumerate(pos_list):
        command = f"C E IA{index + 1}M{init_pos},R"
        move_motor(conn, index + 1, init_pos)
        print(f"Motor {index + 1} initialized")
    return True

# Take measurement of antenna
def measure_vals(conn, min_freq, max_freq, stim_pwr, ifbw, n_points):
    conn.cmd(":DEV:MODE VNA")
    conn.cmd(":VNA:SWEEP FREQUENCY")
    conn.cmd(f":VNA:STIM:LVL {stim_pwr}")
    conn.cmd(f":VNA:ACQ:IFBW {ifbw}")
    conn.cmd(f":VNA:ACQ:AVG {avg_pts}")
    conn.cmd(f":VNA:ACQ:POINTS {n_points}")
    conn.cmd(f":VNA:FREQ:START {min_freq}")
    conn.cmd(f":VNA:FREQ:STOP {max_freq}")
    conn.cmd(f"VNA:ACQuisition:SINGLE TRUE")
    
    while conn.query(":VNA:ACQ:FIN?") == "FALSE":
        time.sleep(0.1)

    read = conn.query(":VNA:TRACE:DATA? S21")
    read = conn.parse_trace_data(read)
    data = []
    for pair in read:
        data.append(pair[1])
    return np.array(data)

if __name__ == "__main__":
    # Initialize peripherals
    vna_gui = subprocess.Popen(
        "exec ~" + VNA_PATH,
        stdout=subprocess.PIPE, 
        shell=True)
    while True:
        gui_str = vna_gui.stdout.readline()
        if "[info] Connected to" in gui_str:
            break

    vna = libreVNA("localhost", 19542)
    vna.cmd(":DEV:CONN")
    dev = vna.query(":DEV:CONN?")
    if dev == "Not connected":
        print("Not connected to any device, aborting")
        exit(-1)
    else:
        print(f"Connected to VNA {dev}, initializing motors")

    motor = serial.Serial(
        port="/dev/ttyUSB0",
        baudrate=9600,
        parity=serial.PARITY_NONE,
        stopbits=1,
        bytesize=8,
        timeout=0.1
    )

    if motor_ready(motor):
        init_motors(motor, init_motor_positions)
    else:
        print("Cannot connect to motor, aborting")
        exit(-1)

    # Collect data
    print("Starting collection")
    measurements = np.empty((n_angles, n_freqs), dtype=np.complex128)
    angle_steps = np.floor(np.linspace(0, steps_per_rev, n_angles, endpoint=False))
    for index, angle_step in enumerate(angle_steps):
        move_motor(motor, MOTOR_DUT, angle_step)
        data = measure_vals(
            vna, 
            freq_min, 
            freq_max, 
            out_power, 
            if_bandwidth,
            n_freqs)
        measurements[index,:] = data
        print(f"Swept {index + 1}/{n_angles}")
    vna_gui.kill()

    # Plot data
    print("Finished collection, plotting")
    np.savetxt("collection.csv", measurements, delimiter=",")
    angles = np.linspace(0, 2 * np.pi, n_angles, endpoint=False)
    angles = np.append(angles, 2 * np.pi - 1e-9)
    freqs = np.linspace(freq_min, freq_max, n_freqs)
    for index, freq in enumerate(freqs):
        fig, ax = plt.subplots(subplot_kw={"projection": "polar"})
        vals = 20 * np.log(np.abs(measurements[:,index]))
        norm_vals = vals - np.max(vals)
        norm_vals = np.append(norm_vals, norm_vals[0])
        ax.plot(angles, norm_vals)
        ax.grid(True)
        ax.set_title(f"Radiation Pattern for {freq / 1e6:.3f} MHz")
        plt.savefig(f"plot{index}.png")
