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


class Scene_node:
    
    def __init__(self):
        self.eye_pub = rospy.Publisher("/eye_status", UInt16, queue_size=1)
        self.led_blink_pub = rospy.Publisher("/led_blink_time", UInt16, queue_size=1)
        self.led_duration = rospy.Publisher("/led_duration", UInt16, queue_size=1)
        self.led_mode = rospy.Publisher("/led_mode", UInt16, queue_size=1)
        self.led_rainbow_delta_hue = rospy.Publisher("/led_rainbow_delta_hue", UInt16, queue_size=1)
        self.led_rgb = rospy.Publisher("/led_rgb", ColorRGBA, queue_size=1)
        #led_blink_pub = rospy.Publisher("/led_blink_time", UInt16, queue_size=1)
        #led_duration = rospy.Publisher("/led_duration", UInt16, queue_size=1)
        #led_mode = rospy.Publisher("/led_mode", UInt16, queue_size=1)
        #led_rainbow_delta_hue = rospy.Publisher("/led_rainbow_delta_hue", UInt16, queue_size=1)
        #led_rgb = rospy.Publisher("/led_rgb", ColorRGBA, queue_size=1)
        
    def eye(self,mode=0):
        mode_msg = UInt16()
        mode_msg.data = mode
        
        self.eye_pub.publish(mode_msg)

    def cheek_led(self,r,g,b,brightness=10,mode=1,blink=3,duration=1,rainbow_hue=1):
        
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

    def ume_led(self,r,g,b,brightness=10,mode=1,blink=3,duration=1,rainbow_hue=1):
            
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
    
