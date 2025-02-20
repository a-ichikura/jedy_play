#x#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

import rospy
import json
import os
import threading
from enum import Enum
from std_msgs.msg import String
from std_msgs.msg import UInt16
from std_msgs.msg import ColorRGBA 
import random

import control_msgs.msg
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

robot_name = rospy.get_param("/robot_name")
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

def servo_on():
    ri.servo_on()

def servo_off():
    ri.servo_off()

def act(act_name, json_filepath, n_split=None):
    ri.servo_on()
    # json_filepath = "/home/leus/Downloads/kashiwagi_movie.json"
    if os.path.exists(json_filepath):
        try:
            with open(json_filepath) as f:
                motion_dict = json.load(f)
        except json.JSONDecodeError as e:
            print(e)

        if len(motion_dict) > 0:
            angles = motion_dict[act_name]
            print(angles)
            if len(angles) > 0:
                ri.angle_vector(angles[0], 1)
                ri.wait_interpolation()
            new_angles = angles[1:]
            if n_split is not None:
                new_angles = new_angles[::n_split]
            for av in new_angles:
                ri.angle_vector(av, 0.1)
                # ri.wait_interpolation()
                rospy.sleep(0.05)
        ri.servo_off()
    else:
        print("There is not such file.")

def act_random(act_name, json_filepath, n_split=None):
    ri.servo_on()
    # json_filepath = "/home/leus/Downloads/kashiwagi_movie.json"
    if os.path.exists(json_filepath):
        try:
            with open(json_filepath) as f:
                motion_dict = json.load(f)
        except json.JSONDecodeError as e:
            print(e)

        add_rd_2 = random.uniform(-0.5,0.5)
        add_rd_4 = random.uniform(-0.5,0.5)
        #print("add_rd_2:{}".format(add_rd_2))
        if len(motion_dict) > 0:
            angles = motion_dict[act_name]
            myangles = angles[0]
            #print(angles)
            if len(angles) > 0:
                ##ここで最初の関節角度を送っている
                myangles[1] += add_rd_2
                myangles[4] += add_rd_4
                ri.angle_vector(myangles, 1)
                ri.wait_interpolation()
            new_angles = angles[1:]
            if n_split is not None:
                new_angles = new_angles[::n_split]
            for av in new_angles:
                ##ここで関節角度を送っている
                av[1] += add_rd_2
                av[4] += add_rd_4
                ri.angle_vector(av, 0.1)
                # ri.wait_interpolation()
                rospy.sleep(0.05)
        ri.servo_off()
    else:
        print("There is not such file.")
    
    
