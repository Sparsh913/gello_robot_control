import os
import sys
import time
import math
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from xarm.wrapper import XArmAPI

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
        ip = '192.168.1.213' #input('Please input the xArm ip address:')
        if not ip:
            print('input error, exit')
            sys.exit(1)
########################################################

arm = XArmAPI(ip, is_radian=True)
arm.motion_enable(enable=True)
arm.set_mode(0)
arm.set_state(state=0)

speed = 1000

# move the J3 to 90 degrees
arm.set_servo_angle(servo_id=3, angle=-90, speed=speed, is_radian=False, wait=True)
arm.set_servo_angle(servo_id=6, angle=0, speed=speed, is_radian=False, wait=True)
# print(f"t={t}, angle={arm.get_servo_angle()[0]}, speed={arm.realtime_joint_speeds}")

# move j6 (-90 to 90) in sinusoidal way
for t in range(100):
    # amplitude = 90 degrees
    angle = 90 * math.sin(t * 0.1)
    arm.set_servo_angle(servo_id=6, angle=angle, speed=speed, is_radian=False, wait=True)
    _, actual_angles = arm.get_servo_angle()
    actual_speeds = arm.realtime_joint_speeds
    print(f"t={t}, angle={actual_angles}, speed={actual_speeds}")
    
arm.disconnect()
