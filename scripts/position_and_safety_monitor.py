#!/usr/bin/env python3

import rospy
import numpy as np
from scipy.spatial.transform import Rotation as R
from apriltag_ros.msg import AprilTagDetectionArray
from geometry_msgs.msg import PointStamped
from std_msgs.msg import Bool
import tf2_ros

class PositionAndSafetyMonitor:
    def __init__(self):
        rospy.init_node("position_and_safety_monitor")
        self.tag_sub = rospy.Subscriber("/tag_detections", AprilTagDetectionArray, self.tag_callback)
        self.position_pub = rospy.Publisher("/coarse_position", PointStamped, queue_size=10)
        self.safety_pub = rospy.Publisher("/is_safe", Bool, queue_size=10)

        self.tag_positions = {
            100: (0.00, 0.00), 101: (0.00, 0.28), 102: (0.00, 0.57), 103: (0.00, 0.85), 104: (0.00, 1.14),
            105: (0.25, 0.00), 106: (0.25, 0.28), 107: (0.25, 0.57), 108: (0.25, 0.85), 109: (0.25, 1.14),
            110: (0.50, 0.00), 111: (0.50, 0.28), 112: (0.50, 0.57), 113: (0.50, 0.85), 114: (0.50, 1.14),
        }

        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer)

        self.x_min = -0.05
        self.x_max = 0.55
        self.y_min = -0.05
        self.y_max = 1.19

        self.last_safe_time = rospy.Time.now()
        self.safe_timeout = rospy.Duration(1.0)

        rospy.sleep(2.0)  # TF安定化待ち

    def tag_callback(self, msg):
        if not msg.detections:
            if rospy.Time.now() - self.last_safe_time > self.safe_timeout:
                self.safety_pub.publish(Bool(False))
            return

        est_positions = []
        weights = []

        try:
            tf_camera_to_base = self.tf_buffer.lookup_transform(
                "camera_color_optical_frame", "base_link", rospy.Time(0), rospy.Duration(0.5)
            )
        except Exception as e:
            rospy.logwarn(f"[TF ERROR] TF lookup failed: {e}")
            return

        for detection in msg.detections:
            tag_id = detection.id[0]
            if tag_id not in self.tag_positions:
                continue

            try:
                tag_pose = detection.pose.pose.pose
                tag_world_xy = self.tag_positions[tag_id]
                est_x, est_y = self.estimate_base_position_from_tag_pose(tag_pose, tag_world_xy, tf_camera_to_base)

                distance = max(np.linalg.norm([
                    tag_pose.position.x, tag_pose.position.y, tag_pose.position.z
                ]), 0.001)
                weight = 1.0 / (distance ** 2)

                est_positions.append((est_x, est_y))
                weights.append(weight)

            except Exception as e:
                rospy.logwarn(f"[EST ERROR] Failed for tag {tag_id}: {e}")
                continue

        if not est_positions:
            rospy.logwarn("[WARN] No valid tag-based estimates available.")
            return

        base_x = sum(w * pos[0] for pos, w in zip(est_positions, weights)) / sum(weights)
        base_y = sum(w * pos[1] for pos, w in zip(est_positions, weights)) / sum(weights)

        point = PointStamped()
        point.header.frame_id = "place-0"
        point.header.stamp = rospy.Time.now()
        point.point.x = base_x
        point.point.y = base_y
        point.point.z = 0.0
        self.position_pub.publish(point)

        is_safe = self.x_min <= base_x <= self.x_max and self.y_min <= base_y <= self.y_max
        self.safety_pub.publish(Bool(is_safe))

        #rospy.loginfo(f"[INFO] Estimated base_link in place-0: x={base_x:.3f}, y={base_y:.3f}")

        if is_safe:
            self.last_safe_time = rospy.Time.now()

    def estimate_base_position_from_tag_pose(self, tag_pose, tag_world_xy, tf_camera_to_base):
        # orientation → 回転行列
        rot = R.from_quat([
            tag_pose.orientation.x,
            tag_pose.orientation.y,
            tag_pose.orientation.z,
            tag_pose.orientation.w
        ])
        T_tag_to_cam = np.eye(4)
        T_tag_to_cam[:3, :3] = rot.as_matrix()
        T_tag_to_cam[:3, 3] = [
            tag_pose.position.x,
            tag_pose.position.y,
            tag_pose.position.z
        ]

        # カメラの位置をタグ基準で求める
        T_cam_in_tag = np.linalg.inv(T_tag_to_cam)
        cam_in_tag = T_cam_in_tag[:3, 3]

        cam_world_x = tag_world_xy[0] + cam_in_tag[0]
        cam_world_y = tag_world_xy[1] + cam_in_tag[1]

        dx = tf_camera_to_base.transform.translation.x
        dy = tf_camera_to_base.transform.translation.y

        base_world_x = cam_world_x + dx
        base_world_y = cam_world_y + dy

        return base_world_x, base_world_y

if __name__ == "__main__":
    PositionAndSafetyMonitor()
    rospy.spin()






