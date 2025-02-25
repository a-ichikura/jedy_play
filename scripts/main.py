import rospy

from module import Module_node
#from jedymodel import *
from ability import play_low,play_middle,play_high,greeting
import time

if __name__ == '__main__':
    module = Module_node()
    time.sleep(3)

    try:
        while not rospy.is_shutdown():
            user_input = input("Enter 'low','middle' or 'high' (or Ctrl+C to exit): ").strip().lower()
            if user_input == "low":
                play_low(module)
            elif user_input == "middle":
                play_middle(module)
            elif user_input == "high":
                play_high(module)
            elif user_input == "greeting":
                greeting(module)
            else:
                print("Invalid input. Please enter 'low','middle' or 'high'.")
    except KeyboardInterrupt:
        print("\nShutting down.")
