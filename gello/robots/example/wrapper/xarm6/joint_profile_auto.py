import numpy as np
import matplotlib.pyplot as plt
import os

def plot_joint_profile(
    actual_angles, commanded_angles, actual_speeds, commanded_speeds, actual_accelerations, 
    commanded_accelerations, timestamps, motion_type
    ):
    """Generate plot and save in current directory"""
    fig, axs = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    
    # Plot joint angles
    axs[0].plot(timestamps, actual_angles, label='Actual Angles', color='blue')
    axs[0].plot(timestamps, commanded_angles, label='Commanded Angles', color='orange')
    axs[0].set_ylabel('Angle (radians)')
    axs[0].legend()
    axs[0].grid(True)
    axs[0].set_title('Joint Angles')
    
    # Plot joint speeds
    axs[1].plot(timestamps, actual_speeds, label='Actual Speeds', color='green')
    axs[1].plot(timestamps, commanded_speeds, label='Commanded Speeds', color='red')
    axs[1].set_ylabel('Speed (radians/second)')
    axs[1].legend()
    axs[1].grid(True)
    axs[1].set_title('Joint Speeds')
    
    # Plot joint accelerations
    axs[2].plot(timestamps, actual_accelerations, label='Actual Accelerations', color='purple')
    axs[2].plot(timestamps, commanded_accelerations, label='Commanded Accelerations', color='orange')
    axs[2].set_ylabel('Acceleration (radians/second^2)')
    axs[2].legend()
    axs[2].grid(True)
    axs[2].set_xlabel('Time (seconds)')
    
    plt.tight_layout()
    
    # Save plot in current directory with motion type
    plt.savefig(f'joint_profile_{motion_type}.png', dpi=300, bbox_inches='tight')
    plt.close()

def process_log_file(log_file_path):
    """Process a single log file and generate plot"""
    timestamps = []
    actual_angle_wrist = []
    actual_speed_wrist = []
    actual_acceleration_wrist = []
    commanded_angle_wrist = []
    commanded_speed_wrist = []
    commanded_acceleration_wrist = []
    
    # Determine motion type from log file name
    motion_type = "sine" if "sine" in log_file_path else \
                 "constant" if "constant" in log_file_path and "pause" not in log_file_path else \
                 "constant_with_pause"
    
    with open(log_file_path, "r") as f:
        for line in f:
            parts = line.split("; ")
            timestamp = float(parts[0].split(", ")[1])
            # Normalize timestamps to start at 0
            if not timestamps:
                start_time = timestamp
            timestamps.append(timestamp - start_time)
            
            actual_angles = parts[0].split(": ")[1].split(", ")
            actual_speeds = parts[1].split(": ")[1].split(", ")
            actual_accelerations = parts[3].split(": ")[1].split(", ")
            commanded_angles = parts[4].split(": ")[1].split(", ")
            commanded_speeds = parts[5].split(": ")[1].split(", ")
            commanded_accelerations = parts[6].split(": ")[1].split(", ")
            
            actual_angle_wrist.append(float(actual_angles[5]))
            actual_speed_wrist.append(float(actual_speeds[5]))
            actual_acceleration_wrist.append(float(actual_accelerations[5]))
            commanded_angle_wrist.append(float(commanded_angles[5]))
            commanded_speed_wrist.append(float(commanded_speeds[5]))
            commanded_acceleration_wrist.append(float(commanded_accelerations[5]))
    
    plot_joint_profile(
        actual_angle_wrist, commanded_angle_wrist,
        actual_speed_wrist, commanded_speed_wrist,
        actual_acceleration_wrist, commanded_acceleration_wrist,
        timestamps, motion_type
    )

if __name__ == "__main__":
    # Look for log files in current directory
    for file in os.listdir('.'):
        if file.startswith('joint_log_'):
            process_log_file(file)
            print(f"Generated plot for {file}")