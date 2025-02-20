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

import control_msgs.msg
import numpy as np

import actionlib
import actionlib_msgs.msg
import random

class Module_node:
    
    def __init__(self):
        self.led_blink_pub = rospy.Publisher("/led_blink_time", UInt16, queue_size=1)
        self.led_duration = rospy.Publisher("/led_duration", UInt16, queue_size=1)
        self.led_mode = rospy.Publisher("/led_mode", UInt16, queue_size=1)
        self.led_rainbow_delta_hue = rospy.Publisher("/led_rainbow_delta_hue", UInt16, queue_size=1)
        self.led_rgb = rospy.Publisher("/led_rgb", ColorRGBA, queue_size=1)
        self.sound_pub = rospy.Publisher("/jedy_voice",String,queue_size=1)

    def led(self,r,g,b,brightness=10,mode=1,blink=3,duration=1,rainbow_hue=1):
        
        color = ColorRGBA()
        color.r = r
        color.g = g
        color.b = b
        color.a = brightness
        
        blink_msg = UInt16()
        duration_msg = UInt16()
        mode_msg = UInt16()
        rainbow_hue_msg = UInt16()
        
        blink_msg.data = blink
        duration_msg.data = duration
        mode_msg.data = mode
        rainbow_hue_msg.data = rainbow_hue
        
        self.led_blink_pub.publish(blink_msg)
        self.led_duration.publish(duration_msg)
        self.led_mode.publish(mode_msg)
        self.led_rainbow_delta_hue.publish(rainbow_hue_msg)
        self.led_rgb.publish(color)

    def sound(self,sound_name):
        sound_msg = String()
        sound_msg.data = sound_name
        self.sound_pub.publish(sound_msg)
        
    def color_change(self,brightness,randomness,r=0,g=0,b=0):
        if brightness <= 0:
            self.led(r,g,b,brightness=brightness)
            return
        if randomness:
            color_list = [[255,0,0],[0,255,0],[0,0,255]]
            color = random.choice(color_list)
            self.led(color[0],color[1],color[2],brightness=brightness)
        else:
            self.led(r,g,b,brightness=brightness)
