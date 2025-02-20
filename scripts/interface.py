#!/usr/bin/env python

import control_msgs.msg
import rospy
from skrobot.interfaces.ros.base import ROSRobotInterfaceBase
from skrobot.model import RobotModel
from skrobot.viewers import TrimeshSceneViewer
from skrobot.utils.urdf import resolve_filepath
import numpy as np

import actionlib
import actionlib_msgs.msg
from kxr_controller.msg import ServoOnOffAction
from kxr_controller.msg import ServoOnOffGoal
from kxr_controller.kxr_interface import KXRROSRobotInterface
from kxr_models.download_urdf import download_urdf_mesh_files

#from save_angle_vector import save_angle_vector_mode
robot_name = rospy.get_param("/robot_name")


def save_angle_vector_mode():
    ri.servo_off()
    angles = []
    while True:
        ret = input("save current angle?")
        ret = ret.lower()
        if ret == "q" or ret == "quite" or ret == "no":
            break
        if ret == "yes" or ret == "y":
            angles.append(ri.angle_vector())
    ri.servo_on()
    # import ipdb
    # ipdb.set_trace()
    print(angles)
    for av in angles:
        ri.angle_vector(av, 0.1)
        ri.wait_interpolation()
        print(1)


rospy.init_node('interface_controller')
r = RobotModel()
urdf_path = resolve_filepath("", "package://jedy_description/urdf/" + robot_name + ".urdf")
print(urdf_path)
with open(urdf_path) as f:
    #r.load_urdf_from_robot_description(f)
    r.load_urdf_file(f)

v = TrimeshSceneViewer()
v.add(r)
v.show()
print(r.joint_list)
for j in r.joint_list:
    if j.max_joint_velocity == 0.0:
        j.max_joint_velocity = 10.0
namespace = ""
#download_urdf_mesh_files(namespace)
ri = KXRROSRobotInterface(r, namespace=None,controller_timeout=10)
