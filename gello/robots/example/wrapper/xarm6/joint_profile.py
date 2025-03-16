import numpy as np
import matplotlib.pyplot as plt
import os

def plot_joint_profile(
    actual_angles, commanded_angles, actual_speeds, commanded_speeds, actual_accelerations, 
    commanded_accelerations, timestamps, motion_type
    ):
    fig, axs = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    fig.suptitle('Joint Angles, Speeds, and Accelerations Over Time')

    # Plot joint angles
    axs[0].plot(timestamps, actual_angles, label='Actual Angles', color='blue')
    axs[0].plot(timestamps, commanded_angles, label='Commanded Angles', color='orange')
    axs[0].set_ylabel('Angle (radians)')
    axs[0].legend()
    axs[0].grid()
    axs[0].set_title('Joint Angles')
    
    # Plot joint speeds
    axs[1].plot(timestamps, actual_speeds, label='Actual Speeds', color='green')
    # slope of actual curve
    # slope_actual = np.gradient(actual_angles, timestamps)
    # print average slope
    # print(f"Average slope of actual curve: {np.mean(slope_actual)}")
    axs[1].plot(timestamps, commanded_speeds, label='Commanded Speeds', color='red')
    axs[1].set_ylabel('Speed (radians/second)')
    axs[1].legend()
    axs[1].grid()
    axs[1].set_title('Joint Speeds')
    
    # Plot joint accelerations
    axs[2].plot(timestamps, actual_accelerations, label='Actual Accelerations', color='purple')
    axs[2].plot(timestamps, commanded_accelerations, label='Commanded Accelerations', color='orange')
    axs[2].set_ylabel('Acceleration (radians/second^2)')
    axs[2].legend()
    axs[2].grid()
    axs[2].set_xlabel('Time (seconds)')
    plt.tight_layout()
    plt.savefig(f'joint_profile_{motion_type}.png')
    plt.show()
        

if __name__ == "__main__":
    # parse txt log file to retrieve joint angles, speeds, and accelerations, along with timestamps
    # and save the plot as an image
    motion_type = "sine"
    log_file_path = f"/home/uas-laptop/Kantor_Lab/sparsh/gello_software/joint_log_{motion_type}.txt"
    # text file of this format:
    # 1, 220.792627, Actual Angles: 0.0, 0.0, -1.570796012878418, 0.0, 0.0, 1.534250259399414, 0.0; Actual Speeds: 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0; Actual Efforts: 1.305232773093554e-15, -15.513633728027344, -12.161165237426758, -0.19442638754844666, -0.5657081007957458, 0.0004125152190681547, 0.0; Actual Accelerations: 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0; Commanded Angles: 0.0, 0.0, -1.570796, 0.0, 0.0, 1.5248644074734696, 0.0; Commanded Speeds: 0.0, 0.0, 0.0, 0.0, 0.0, 0.6981317007977318, 0.0; Commanded Accelerations: 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
    # 2, 220.806071, Actual Angles: 0.0, 0.0, -1.570796012878418, 0.0, 0.0, 1.5342330932617188, 0.0; Actual Speeds: 0.0, 0.0, -8.716916077844417e-10, 0.0, 0.0, -0.003739491803571582, 0.0; Actual Efforts: 1.305232773093554e-15, -15.513633728027344, -12.161165237426758, -0.19442638754844666, -0.5657081007957458, 0.0004125152190681547, 0.0; Actual Accelerations: 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0; Commanded Angles: 0.0, 0.0, -1.570796, 0.0, 0.0, 1.5072693676892586, 0.0; Commanded Speeds: 0.0, 0.0, 0.0, 0.0, 0.0, 0.6981317007977318, 0.0; Commanded Accelerations: 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
    # extract joint angles from the log file for joint 6
    timestamps = []
    actual_angle_wrist = []
    actual_speed_wrist = []
    actual_acceleration_wrist = []
    
    commanded_angle_wrist = []
    commanded_speed_wrist = []
    commanded_acceleration_wrist = []
    
    with open(log_file_path, "r") as f:
        for line in f:
            parts = line.split("; ")
            timestamp = parts[0].split(", ")[1]
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
            timestamps.append(float(timestamp))
            
    # Use low pass filtering to smooth the actual data
    # actual_angle_wrist = np.convolve(actual_angle_wrist, np.ones(20)/20, mode='same')
    # actual_speed_wrist = np.convolve(actual_speed_wrist, np.ones(20)/20, mode='same')
    # actual_acceleration_wrist = np.convolve(actual_acceleration_wrist, np.ones(20)/20, mode='same')
            
    # plot joint angles, speeds, and accelerations over time both actual and commanded
    plot_joint_profile(actual_angle_wrist, commanded_angle_wrist, actual_speed_wrist, commanded_speed_wrist, actual_acceleration_wrist, commanded_acceleration_wrist, timestamps, motion_type)