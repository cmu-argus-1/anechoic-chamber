#!/usr/bin/env python3
import time
import os
import serial
import numpy as np
import subprocess
import matplotlib.pyplot as plt
from libreVNA import libreVNA
from measure_funcs import *

if __name__ == "__main__":
    # Load configuration
    config = load_configs()
    print(config)

    # Initialize peripherals
    vna_gui = subprocess.Popen(
        "exec ~" + config["vna_path"],
        stdout=subprocess.PIPE, 
        shell=True)
    os.set_blocking(vna_gui.stdout.fileno(), False)
    start = time.time()
    while True:
        for i in range(2):
            gui_str = vna_gui.stdout.readline()
        if "[info] Connected to" in str(gui_str):
            break
        if time.time() > start + 5:
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
        move_motor(motor, config, config["init_motor_pos"])
    else:
        print("Cannot connect to motor, aborting")
        exit(-1)

    # Collect data
    print("Starting collection")
    measurements = np.empty((
        config["n_angles"], 
        config["pts_2"]), 
        dtype=np.complex128)
    angle_steps = np.floor(np.linspace(
        0, 
        config["steps_per_rev"], 
        config["n_angles"], 
        endpoint=False))
    
    for index, angle_step in enumerate(angle_steps):
        move_motor(motor, config, angle_step)
        data = measure_vals(vna, config)
        measurements[index, :] = data
        print(f"Swept {index + 1}/{config['n_angles']}")
    vna_gui.kill()

    # Plot data
    print("Finished collection, saving measurements and plots")
    
    timestamp = time.strftime("%y-%m-%d-%H:%M:%S")
    np.savetxt(f"collection{timestamp}.csv", measurements, delimiter=",")

    angles = np.linspace(0, 2 * np.pi, config["n_angles"], endpoint=False)
    angles = np.append(angles, 2 * np.pi - 1e-9)
    fig, ax = plt.subplots(subplot_kw={"projection": "polar"})
    vals = 20 * np.log(np.abs(measurements))
    vals = np.average(vals, axis=1)
    norm_vals = vals - np.max(vals)
    norm_vals = np.append(norm_vals, norm_vals[0])

    ax.plot(angles, norm_vals)
    ax.grid(True)
    ax.set_title(f"Radiation Pattern for {config['freq'] / 1e6:.3f} MHz")
    ax.set_ylim([min(config['plot_min'], np.min(vals)),0])
    plt.savefig(f"plot{timestamp}.png")
