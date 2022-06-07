#!/usr/bin/env python
import roslaunch
import rospy
import Database
from std_msgs.msg import Int16

from sensor_msgs.msg import LaserScan

con_scan = 0   
launch = 0 
        
def scanner_callback(data):
        global con_scan
        con_scan = 0

#/home/agvs/cw/src/sick_safetyscanners/launch/sick_safetyscanners.launch

if __name__ == '__main__':
    rospy.init_node('Inicia_Scan', anonymous=False)
    rospy.Subscriber("/sick_safetyscanners/scan", LaserScan, scanner_callback)
    
    uuid = roslaunch.rlutil.get_or_generate_uuid(None, False)
    roslaunch.configure_logging(uuid)
    launch = roslaunch.parent.ROSLaunchParent(uuid, ["/opt/ros/noetic/share/sick_safetyscanners/launch/sick_safetyscanners.launch"])


    #rospy.loginfo("started")
    launch.start()

    rate = rospy.Rate(1)
    con_scan = 0

    while not rospy.is_shutdown():
    
        con_scan += 1
        
        if con_scan > 5:
               # launch.stop()
                launch.start()
                con_scan = 0
                
                  
        rate.sleep()
