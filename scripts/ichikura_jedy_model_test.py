import numpy as np
import rospy
from skrobot.models.urdf import RobotModelFromURDF
from skrobot.coordinates import CascadedCoords
from skrobot.model import RobotModel
from skrobot.coordinates import Coordinates
from skrobot.utils.urdf import resolve_filepath
import time
from cached_property import cached_property
from jedy_interface import IJedyROSRobotInterface

# from jedymodel import *

rospy.init_node("ichikura_jedy_model")

robot_name = rospy.get_param("/robot_name", "jedy")

class IchikuraJedy(RobotModelFromURDF):

    def __init__(self, *args, **kwargs):
        super(IchikuraJedy, self).__init__(*args, **kwargs)
        self.rarm_end_coords = CascadedCoords(
            parent=self.rarm_link5,
            name='rarm_end_coords')
        self.rarm_end_coords.rotate(np.pi / 2, 'y')
        self.rarm_end_coords.translate([0.05, 0.0, 0.0])
        self.larm_end_coords = CascadedCoords(
            parent=self.larm_link5,
            name='larm_end_coords')
        self.larm_end_coords.rotate(np.pi / 2, 'y')
        self.larm_end_coords.translate([0.05, 0.0, 0.0])
        self.reset_pose()

    @cached_property
    def default_urdf_path(self):
        return resolve_filepath("", "package://kxr_humanoid_movebase_ichikura/urdf/" + robot_name + ".urdf")

    def reset_pose(self):
        self.rarm_joint0.joint_angle(np.deg2rad(30))
        self.rarm_joint1.joint_angle(np.deg2rad(0))
        self.rarm_joint2.joint_angle(np.deg2rad(0))
        self.rarm_joint3.joint_angle(np.deg2rad(-120))
        self.rarm_joint4.joint_angle(np.deg2rad(0))
        self.rarm_gripper_joint.joint_angle(np.deg2rad(0))
        self.larm_joint0.joint_angle(np.deg2rad(30))
        self.larm_joint1.joint_angle(np.deg2rad(0))
        self.larm_joint2.joint_angle(np.deg2rad(0))
        self.larm_joint3.joint_angle(np.deg2rad(-60))
        self.larm_joint4.joint_angle(np.deg2rad(0))
        self.larm_gripper_joint.joint_angle(np.deg2rad(0))

    @cached_property
    def rarm(self):
        link_names = ['rarm_link{}'.format(i) for i in range(0, 6)]
        links = [getattr(self, n) for n in link_names]
        joints = [l.joint for l in links]
        model = RobotModel(link_list=links, joint_list=joints)
        model.end_coords = self.rarm_end_coords
        return model

    @cached_property
    def larm(self):
        link_names = ['larm_link{}'.format(i) for i in range(0, 6)]
        links = [getattr(self, n) for n in link_names]
        joints = [l.joint for l in links]
        model = RobotModel(link_list=links, joint_list=joints)
        model.end_coords = self.larm_end_coords
        return model

    


robot_model = IchikuraJedy()
robot_model.rotate(- np.pi / 2, 'z')
robot_model.rotate(np.pi / 2, 'x')

print(robot_model.joint_list)
ri = IJedyROSRobotInterface(robot_model, namespace=None,controller_timeout=10)
print(1)

#from skrobot.viewers import TrimeshSceneViewer
#from skrobot.model import Axis
#import numpy as np

#viewer = TrimeshSceneViewer()
#viewer.add(robot_model)
#viewer.show()
#axis = Axis.from_coords(robot_model.rarm_end_coords)
#viewer.add(axis)

print(2)

robot_model.reset_pose()

print(3)

joint_angle = robot_model.angle_vector()

print(4)

print("joint angle:{}".format(joint_angle))

ri.servo_on()

