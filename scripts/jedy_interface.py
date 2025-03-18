
import control_msgs.msg
from kxr_controller.kxr_interface import KXRROSRobotInterface


class IJedyROSRobotInterface(KXRROSRobotInterface):

    @property
    def fullbody_controller(self):
        cont_name = "fullbody_controller"
        return {
            "controller_type": cont_name,
            "controller_action": cont_name + "/follow_joint_trajectory",
            "controller_state": cont_name + "/state",
            "action_type": control_msgs.msg.FollowJointTrajectoryAction,
            "joint_names": self.joint_names,
        }

    @property
    def larm_controller(self):
        return dict(
            controller_type='larm_controller',
            controller_action='larm_controller/follow_joint_trajectory',
            controller_state='larm_controller/state',
            action_type=control_msgs.msg.FollowJointTrajectoryAction,
            joint_names=['larm_joint0',
                         'larm_joint1',
                         'larm_joint2',
                         'larm_joint3',
                         'larm_joint4',
                         'larm_gripper_joint'])

    @property
    def rarm_controller(self):
        return dict(
            controller_type='rarm_controller',
            controller_action='rarm_controller/follow_joint_trajectory',
            controller_state='rarm_controller/state',
            action_type=control_msgs.msg.FollowJointTrajectoryAction,
            joint_names=['rarm_joint0',
                         'rarm_joint1',
                         'rarm_joint2',
                         'rarm_joint3',
                         'rarm_joint4',
                         'rarm_gripper_joint'])

    @property
    def head_controller(self):
        return dict(
            controller_type='head_controller',
            controller_action='head_controller/follow_joint_trajectory',
            controller_state='head_controller/state',
            action_type=control_msgs.msg.FollowJointTrajectoryAction,
            joint_names=['head_joint0','head_joint1'])

    def default_controller(self):
        """Overriding default_controller.

        Returns
        -------
        List of limb controller : list
        """
        return [
            self.larm_controller,
            self.rarm_controller,
            self.head_controller,
        ]
