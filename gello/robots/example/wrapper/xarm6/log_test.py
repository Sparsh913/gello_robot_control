import threading
import queue
import time
import numpy as np
import cv2
# import pyrealsense2 as rs
from gello.cameras import RealSenseCamera, get_device_ids
from xarm.wrapper import XArmAPI
import os
import sys
import matplotlib.pyplot as plt
from collections import deque
import argparse

#######################################################
"""
Just for test example
"""
if len(sys.argv) >= 2:
    ip = sys.argv[1]
else:
    try:
        from configparser import ConfigParser
        parser = ConfigParser()
        parser.read('../robot.conf')
        ip = parser.get('xArm', 'ip')
    except:
        ip = "192.168.1.213" #input('Please input the xArm ip address:')
        if not ip:
            print('input error, exit')
            sys.exit(1)
########################################################

# Initialize xArm API
ip = "192.168.1.213"  # Replace with your xArm's IP
arm = XArmAPI(ip, is_radian=True)

# Enable robot motion
arm.motion_enable(enable=True)
arm.set_mode(4)  # Velocity control mode
arm.set_state(state=0)

# Shared queue for synchronization
sync_queue = queue.Queue()
image_counter = 0  # Global image counter for consistent naming
terminate = False
speed = 40  # Constant speed command
commanded_angles = arm.get_servo_angle()[1]
commanded_speeds = np.array([0, 0, 0, 0, 0, np.deg2rad(speed), 0])
commanded_accelerations = np.array([0, 0, 0, 0, 0, 0, 0])

# Tracking previous speeds for acceleration computation
prev_speeds = None
prev_time = None
ctr = 0
device_ids = get_device_ids()
rs = RealSenseCamera(flip=False, device_id=get_device_ids()[0])
time.sleep(4) # wait for camera to start

# args
parser = argparse.ArgumentParser()
parser.add_argument('--motion_type', type=str, default='sinusoidal', help='Motion type: sinusoidal or constant')

args = parser.parse_args()

if args.motion_type == "sinusoidal":
    joint_log_file_path = "joint_log_sine.txt"
    image_log_file_path = "image_log_sine.txt"
    image_folder_path = "images_sine"
elif args.motion_type == "constant":
    joint_log_file_path = "joint_log_constant.txt"
    image_log_file_path = "image_log_constant.txt"
    image_folder_path = "images_constant"
elif args.motion_type == "constant_with_pause":
    joint_log_file_path = "joint_log_constant_with_pause.txt"
    image_log_file_path = "image_log_constant_with_pause.txt"
    image_folder_path = "images_constant_with_pause"
else:
    raise ValueError("Invalid motion type. Choose 'sinusoidal' or 'constant'.")

def camera_thread():
    """Captures images and timestamps from the RealSense camera."""
    # print(f"Found {len(device_ids)} devices")
    # rs = RealSenseCamera(flip=False, device_id=device_ids[0])
    global rs
    while True:
        # Capture image and timestamp
        frame, _ = rs.read()
        timestamp = time.perf_counter()
        # cv2.imshow("Camera Feed", frame[:, :, ::-1])
        # cv2.waitKey(1)
        # cv2.closeAllWindows()

        # Add image data to queue, but only log it later if it matches a robot timestamp
        sync_queue.put(("image", timestamp, frame[:, :, ::-1]))

def robot_thread(motion_type='constant'):
    """Logs actual and commanded joint states, speeds, and computes accelerations."""
    global prev_speeds, prev_time, speed, commanded_angles, terminate, commanded_accelerations, commanded_speeds, ctr
    start_time = time.perf_counter()
    while True:
        timestamp = time.perf_counter()

        # Get actual joint angles and speeds
        # _, actual_angles = arm.get_servo_angle()
        joint_states = arm.get_joint_states()
        code, states = joint_states
        if code == 0:
            actual_angles = states[0]
            actual_speeds = states[1]
            actual_efforts = states[2]
        else:
            actual_angles = None
            actual_speeds = None
            actual_efforts = None
        # actual_speeds = arm.realtime_joint_speeds  # Correct API method
        # print("actual_angles: ", actual_angles)
        # print("actual_speeds: ", actual_speeds)

        # Compute actual accelerations using finite difference
        # commanded_speeds = np.array([0, 0, 0, 0, 0, np.deg2rad(speed), 0])
        if prev_speeds is not None and prev_time is not None:
            delta_t = timestamp - prev_time
            if delta_t > 0:
                actual_accelerations = (np.array(actual_speeds) - np.array(prev_speeds)) / delta_t
                if motion_type == "constant":
                    elapsed_time = timestamp - start_time
                    commanded_angles = commanded_speeds * elapsed_time
                elif motion_type == "constant_with_pause":
                    commanded_angles += delta_t * commanded_speeds
            else:
                actual_accelerations = np.zeros_like(actual_speeds)
                # commanded_angles += np.zeros_like(actual_angles)
        else:
            actual_accelerations = np.zeros_like(actual_speeds)  # First iteration default
            # commanded_angles += np.zeros_like(actual_angles)  # Placeholder

        prev_speeds = actual_speeds
        prev_time = timestamp
        # print(f"commanded angles: {commanded_angles} | actual angles: {actual_angles}")
        # Get commanded joint angles and speeds
        # commanded_angles =  delta_t

        # Assume commanded accelerations are not directly available
        # commanded_accelerations = np.zeros_like(commanded_speeds)  # Placeholder
        if motion_type == 'constant':
            if actual_angles[5] > np.deg2rad(85) or actual_angles[5] < np.deg2rad(-85):
                terminate = True

        # if all([actual_angles, actual_speeds, actual_accelerations, 
        #         commanded_angles, commanded_speeds, commanded_accelerations]):
        if actual_angles is not None and actual_speeds is not None and actual_efforts is not None and actual_accelerations is not None and \
        commanded_angles is not None and commanded_speeds is not None and commanded_accelerations is not None:

            sync_queue.put(("joint", timestamp, actual_angles, actual_speeds, actual_efforts, actual_accelerations,
                            commanded_angles, commanded_speeds, commanded_accelerations))

def command_thread(motion_type: str):
    """Sends movement commands to the robot."""
    # global terminate
    global speed, commanded_angles, commanded_speeds, commanded_accelerations, terminate
    speed = 20  # Constant speed command
    amplitude = np.deg2rad(85)  # Amplitude for sinusoidal movement
    freq = 0.25  # Frequency for sinusoidal movement
    omega = 2 * np.pi * freq
    start_time = time.perf_counter()
    
    if motion_type == "sinusoidal":
        while not terminate:
            # Move the J3 joint to -90 degrees
            # arm.set_servo_angle(servo_id=3, angle=-90, speed=speed, is_radian=False, wait=False)

            # Move the J6 joint to 0 degrees
            # arm.set_servo_angle(servo_id=6, angle=0, speed=speed, is_radian=False, wait=False)
            # J6: sinusoidal movement with amplitude of 90 degrees - max 90 degree in each direction, just for 1 cycle; freq corresponding to speed
            t = time.perf_counter() - start_time
            # print(f"t: {t}")
            if t > 1/freq:
                arm.vc_set_joint_velocity(speeds=[0, 0, 0, 0, 0, 0, 0], is_radian=True, duration=0)
                terminate = True
                break
            # if motion_type == "sinusoidal":
            commanded_angles[5] = amplitude * np.sin(omega * t)
            commanded_speeds[5] = amplitude * omega * np.cos(omega * t)
            speeds = [0, 0, 0, 0, 0, commanded_speeds[5], 0]
            commanded_accelerations[5] = amplitude * omega**2 * np.sin(omega * t)
            arm.vc_set_joint_velocity(speeds=speeds, is_radian=True, duration=0)
            # arm.set_servo_angle(servo_id=6, angle=commanded_angles[5], is_radian=True, wait=False)
            time.sleep(0.02)
        # elif motion_type == "constant":
            # go from 0 to 90 degrees with angular velocity of 0.5 rad/sec
            # time_step = 1/30
            # commanded_angles[5] += (np.deg2rad(speed) * time_step)
            # commanded_speeds[5] = np.deg2rad(speed)
            # commanded_accelerations[5] = 0
            # arm.set_servo_angle(servo_id=6, angle=commanded_angles[5], is_radian=True, wait=False)
            # time.sleep(time_step)
    elif motion_type == "constant":
        # arm.set_servo_angle(servo_id=6, angle=np.deg2rad(87), speed=np.deg2rad(speed), is_radian=True, wait=False)
        speeds = [0, 0, 0, 0, 0, np.deg2rad(speed), 0]
        while not terminate:
            arm.vc_set_joint_velocity(speeds=speeds, is_radian=True, duration=0)
            commanded_speeds[5] = np.deg2rad(speed)
            commanded_accelerations[5] = 0
            
    elif motion_type == "constant_with_pause":
        # 0 to 85 degrees with constant speed , pause for 1 second, then to 0 with constant speed, pause for 1 second, then to -85 degrees with constant speed, pause for 1 second, then to 0 with constant speed
        positive_speeds = [0, 0, 0, 0, 0, np.deg2rad(speed), 0]
        negative_speeds = [0, 0, 0, 0, 0, -np.deg2rad(speed), 0]
        pause_time = 1
        while not terminate:
            while commanded_angles[5] < np.deg2rad(85):
                arm.vc_set_joint_velocity(speeds=positive_speeds, is_radian=True, duration=0)
                commanded_speeds[5] = np.deg2rad(speed)
                commanded_accelerations[5] = 0
                time.sleep(0.02)
                
            # pause for 1 second
            arm.vc_set_joint_velocity(speeds=[0, 0, 0, 0, 0, 0, 0], is_radian=True, duration=0)
            commanded_speeds[5] = 0
            commanded_accelerations[5] = 0
            time.sleep(pause_time)
            
            while commanded_angles[5] >= 0:
                arm.vc_set_joint_velocity(speeds=negative_speeds, is_radian=True, duration=0)
                commanded_speeds[5] = -np.deg2rad(speed)
                commanded_accelerations[5] = 0
                time.sleep(0.02)
                
            # pause for 1 second
            arm.vc_set_joint_velocity(speeds=[0, 0, 0, 0, 0, 0, 0], is_radian=True, duration=0)
            commanded_speeds[5] = 0
            commanded_accelerations[5] = 0
            time.sleep(pause_time)
            
            while commanded_angles[5] > np.deg2rad(-85):
                arm.vc_set_joint_velocity(speeds=negative_speeds, is_radian=True, duration=0)
                commanded_speeds[5] = -np.deg2rad(speed)
                commanded_accelerations[5] = 0
                time.sleep(0.02)
                
            # pause for 1 second
            arm.vc_set_joint_velocity(speeds=[0, 0, 0, 0, 0, 0, 0], is_radian=True, duration=0)
            commanded_speeds[5] = 0
            commanded_accelerations[5] = 0
            time.sleep(pause_time)
            
            while commanded_angles[5] <= 0:
                arm.vc_set_joint_velocity(speeds=positive_speeds, is_radian=True, duration=0)
                commanded_speeds[5] = np.deg2rad(speed)
                commanded_accelerations[5] = 0
                time.sleep(0.02)
                
            # Final stop
            arm.vc_set_joint_velocity(speeds=[0, 0, 0, 0, 0, 0, 0], is_radian=True, duration=0)
            commanded_speeds[5] = 0
            commanded_accelerations[5] = 0
            time.sleep(pause_time)
            terminate = True
            

def logger_thread():
    """Logs synchronized data by matching the closest timestamps."""
    global image_counter
    image_log = deque()
    joint_log = deque()

    while True:
        data = sync_queue.get()  # Get data from queue
        
        if data[0] == "image":
            image_log.append((data[1], data[2]))  # ("image", timestamp, image)
        elif data[0] == "joint":
            joint_log.append((data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8]))  # ("joint", timestamp, actual_angles, actual_speeds, actual_efforts, actual_accelerations, commanded_angles, commanded_speeds, commanded_accelerations)

        # print(f"Image log length: {len(image_log)}, Joint log length: {len(joint_log)}")
        # Find closest match between image & joint data
        while image_log and joint_log:
            img_time, img_data = image_log[0]
            jnt_time, actual_angles, actual_speeds, actual_efforts, actual_accelerations, \
                commanded_angles, commanded_speeds, commanded_accelerations = joint_log.popleft()

            if abs(img_time - jnt_time) < 0.01: # 10 ms tolerance
                image_counter += 1  # Increment image counter for consistent numbering
                filename = f"{image_folder_path}/image_{image_counter}.png"
                cv2.imwrite(filename, img_data)
                # print(f"Saved {filename}")

                # Log timestamp with corresponding image ID
                with open(image_log_file_path, "a") as f:
                    f.write(f"{image_counter}, {jnt_time:.6f}\n")
                    print(f"Logged {image_counter} at {jnt_time:.6f}")

                # Log joint data with corresponding image ID
                with open(joint_log_file_path, "a") as f:
                    print("logging joint data")
                    f.write(f"{image_counter}, {jnt_time:.6f}, "
                            f"Actual Angles: {', '.join(map(str, actual_angles))}; "
                            f"Actual Speeds: {', '.join(map(str, actual_speeds))}; "
                            f"Actual Efforts: {', '.join(map(str, actual_efforts))}; "
                            f"Actual Accelerations: {', '.join(map(str, actual_accelerations))}; "
                            f"Commanded Angles: {', '.join(map(str, commanded_angles))}; "
                            f"Commanded Speeds: {', '.join(map(str, commanded_speeds))}; "
                            f"Commanded Accelerations: {', '.join(map(str, commanded_accelerations))}\n")

                image_log.popleft() # image data has a low sampling rate compared to joint data
            else:
                # print("No close match found, waiting for better data...")
                break  # Wait for a better match

os.makedirs(f"{image_folder_path}", exist_ok=True)
# Start threads
threading.Thread(target=camera_thread, daemon=True).start()
threading.Thread(target=robot_thread, args=(args.motion_type,), daemon=True).start()
threading.Thread(target=logger_thread, daemon=True).start()
threading.Thread(target=command_thread, args=(args.motion_type,), daemon=True).start()

# Keep the main thread alive
while not terminate:
    time.sleep(0.18)
