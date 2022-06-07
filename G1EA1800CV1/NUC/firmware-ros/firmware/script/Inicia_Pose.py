#!/usr/bin/env python
import roslaunch
import rospy

from geometry_msgs.msg import PoseWithCovarianceStamped


con_pose = 0

def pose_callback(data):
        global con_pose
        con_pose = 0


if __name__ == '__main__':
    rospy.init_node('Inicia_Pose', anonymous=False)
    uuid = roslaunch.rlutil.get_or_generate_uuid(None, False)
    roslaunch.configure_logging(uuid)
    launch = roslaunch.parent.ROSLaunchParent(uuid, ["/opt/ros/noetic/share/hector_mapping/launch/mapping_default.launch"])

    rospy.Subscriber("/poseupdate", PoseWithCovarianceStamped, pose_callback)

    #rospy.loginfo("started")
    launch.start()

    rate = rospy.Rate(1)
    con_pose = 0

    while not rospy.is_shutdown():      
        #con_pose += 1
        
        #if con_pose > 10:
                #launch.stop()
        #        launch.start()
        #        con_pose = 0
                
                  
        rate.sleep()
