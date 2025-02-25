#x#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

import rospy
import json
import os
import random
import time
from jedymodel import *
from std_msgs.msg import Bool

def start_draw():
    draw_list = ["draw_1","draw_2","draw_3"]
    motion = random.choice(draw_list)
    print("motion name:{}".format(motion))
    act_random(motion,"/home/leus/jedy_test.json")

def play_low(module):
    #動作開始
    time.sleep(3)
    module.color_change(2,False,255,255,255)
    rospy.loginfo("Start")
    module.sound("help")
    module.color_change(2,True)
    ri.servo_on()
    ri.angle_vector([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,-1.0,0.5,0,0,0,0],1.0,controller_type="head_controller")
    ri.wait_interpolation()
    ri.servo_off()
    time.sleep(10) #10秒待つ(絵の具をつける)
    rospy.loginfo("please press button")
    module.sound("please press button")
    msg = rospy.wait_for_message("/button_ispressed",Bool,timeout=None)
    ri.servo_on()
    ri.angle_vector([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.2,0,0,0,0],1.0,controller_type="head_controller")
    ri.wait_interpolation()
    module.sound("ready")
    ri.servo_off()
    module.led(0,0,0,mode=3)
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
    ri.wait_interpolation()
    ri.servo_off()
    time.sleep(10) #10秒待つ(絵の具をつける)
    rospy.loginfo("please press button")
    module.sound("please press button")
    msg = rospy.wait_for_message("/button_ispressed",Bool,timeout=None)
    servo_on()
    ri.angle_vector([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.2,0,0,0,0],1.0,controller_type="head_controller")
    ri.wait_interpolation()
    module.sound("ready")
    rospy.loginfo("Now ready")
    module.led(0,0,0,mode=3)
    start_draw()
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
    module.led(0,0,0,mode=3)
    rospy.loginfo("Now ready")
    start_draw()
    act("init_pose","/home/leus/jedy_test.json")
    module.sound("joy")
    rospy.loginfo("Done")
    module.color_change(0,False)
    
def greeting(module):
    time.sleep(3)
    module.color_change(2,True)
    msg = rospy.wait_for_message("/button_ispressed",Bool,timeout=None)
    module.led(0,0,0,mode=3)
    servo_on()
    act("byebye","/home/leus/jedy_test.json")
    module.color_change(0,False)
    
