import time
import re
import numpy as np

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
def move_motor(conn, config, pos):
    POS_CHECK = ["", "X", "Y", "Z", "T"]
    pos = int(pos)
    letter = POS_CHECK[config["motor_dut"]]
    conn.write(letter.encode(encoding="ascii"))
    read = conn.readline().decode("ascii")
    current_pos = int(re.findall(r"[+-]\d+", read)[0])

    next_pos = (current_pos - 
        current_pos % config["steps_per_rev"] + 
        pos % config["steps_per_rev"])
    
    command = f"C E IA{config['motor_dut']}M{next_pos},R"
    conn.write(command.encode(encoding="ascii"))
    conn.readline()
    
    while(current_pos % config["steps_per_rev"] != pos):
        time.sleep(0.1)
        conn.write(letter.encode(encoding="ascii"))
        read = conn.readline().decode("ascii")
        current_pos = int(re.findall("[+-]\d+", read)[0])
    return True

# Take measurement of antenna
def measure_vals(conn, config):
    conn.cmd(":DEV:MODE VNA")
    conn.cmd(":VNA:SWEEP FREQUENCY")
    conn.cmd(f":VNA:STIM:LVL {config['stim_pwr']}")
    conn.cmd(f":VNA:ACQ:IFBW {config['if_bandwidth']}")
    conn.cmd(f":VNA:ACQ:AVG {config['pts_1']}")
    conn.cmd(f":VNA:ACQ:POINTS {config['pts_2']}")
    conn.cmd(f":VNA:FREQ:CENT {config['freq']}")
    conn.cmd(f":VNA:FREQ:ZERO")
    conn.cmd(f":VNA:ACQuisition:SINGLE TRUE")
    
    while conn.query(":VNA:ACQ:FIN?") == "FALSE":
        time.sleep(0.1)

    read = conn.query(":VNA:TRACE:DATA? S21")
    read = conn.parse_trace_data(read)
    data = []
    for pair in read:
        data.append(pair[1])
    return np.array(data)

# Load settings from file
def load_configs():
    config_path = ".config"
    config_file = open(config_path)
    config = {}
    line = config_file.readline()
    while line != "":
        var = line.split("🐥")
        if var == []:
            break
        elif var[0] == "vna_path":
            newval = var[1].replace(" ", "")
        else:
            newval = int(var[1])
            if var[0] == "freq" and (newval < 1e5 or newval > 6e9):
                raise ValueError("Frequency must be between 100kHz and 6GHz")
            elif var[0] == "stim_pwr" and (newval < -40 or newval > 0):
                raise ValueError("Stimulus power must between -40 and 0 dBm")
            elif var[0] == "if_bandwidth" and (newval < 10 or newval > 5e4):
                raise ValueError("IF bandwidth must be between 10Hz and 50kHz")
            elif var[0] == "motor_dut" and (newval < 1 or newval > 4):
                raise ValueError("Motor ID must be 1, 2, 3, or 4")
            elif var[0] == "pts_1" and (newval < 1 or newval > 99):
                raise ValueError("VNA-averaged points must be between 1 and 99")
            elif var[0] == "pts_2" and newval < 2:
                raise ValueError("Collection must contain at least 2 points")
        config[var[0]] = newval
        line = config_file.readline()
    config_file.close()
    return config