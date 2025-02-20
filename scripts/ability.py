#x#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

import rospy
import json
import os
import random
import time
from jedymodel import *
from std_msgs.msg import Bool

def play_low(module):
    #動作開始
    time.sleep(3)
    module.color_change(2,False,255,255,255)
    rospy.loginfo("Start")
    module.sound("help")
    module.color_change(2,True)
    ri.servo_on()
    ri.angle_vector([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,-1.0,0.5,0,0,0,0],1.0,controller_type="head_controller")
    ri.servo_off()
    time.sleep(10) #10秒待つ(絵の具をつける)
    rospy.loginfo("please press button")
    msg = rospy.wait_for_message("/button_ispressed",Bool,timeout=None)
    ri.servo_on()
    ri.angle_vector([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.2,0,0,0,0],1.0,controller_type="head_controller")
    module.sound("ready")
    ri.servo_off()
    rospy.loginfo("now drawing")
    time.sleep(10) #10秒待つ(絵を描く)
    module.sound("joy")
    rospy.loginfo("Done")
    module.color_change(0,False)

def play_middle(module):
    #動作開始
    time.sleep(3)
    module.color_change(2,False,255,255,255)
    rospy.loginfo("Start")
    module.sound("help")
    module.color_change(2,True)
    ri.servo_on()
    ri.angle_vector([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,-1.0,0.5,0,0,0,0],1.0,controller_type="head_controller")
    ri.servo_off()
    time.sleep(10) #10秒待つ(絵の具をつける)
    rospy.loginfo("please press button")
    msg = rospy.wait_for_message("/button_ispressed",Bool,timeout=None)
    servo_on()
    ri.angle_vector([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.2,0,0,0,0],1.0,controller_type="head_controller")
    module.sound("ready")
    rospy.loginfo("Now ready")
    act_random("draw_1","/home/leus/jedy_test.json")
    act("init_pose","/home/leus/jedy_test.json")
    module.sound("joy")
    rospy.loginfo("Done")
    module.color_change(0,False)

def play_high(module):
    #動作開始
    time.sleep(3)
    module.color_change(2,False,255,255,255)
    rospy.loginfo("Start")
    module.sound("help")
    module.color_change(2,True)
    ri.servo_on()
    act("coloring","/home/leus/jedy_test.json")
    module.sound("ready")
    rospy.loginfo("Now ready")
    act_random("draw_1","/home/leus/jedy_test.json")
    act("init_pose","/home/leus/jedy_test.json")
    module.sound("joy")
    rospy.loginfo("Done")
    module.color_change(0,False)
    
