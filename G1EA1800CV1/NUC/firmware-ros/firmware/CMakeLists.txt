cmake_minimum_required(VERSION 3.0.2)
project(firmware)


find_package(catkin REQUIRED COMPONENTS
  roscpp
  rospy
  std_msgs
  message_generation
)


## Generate messages in the 'msg' folder
 add_message_files(
   FILES
   entradas.msg
   saidas.msg
 )

## Generate added messages and services with any dependencies listed here
 generate_messages(
   DEPENDENCIES
   std_msgs
 )


catkin_package(
#  INCLUDE_DIRS include
#  LIBRARIES firmware
#  CATKIN_DEPENDS roscpp rospy std_msgs
#  DEPENDS system_lib
   CATKIN_DEPENDS message_runtime
)


include_directories(
# include
  ${catkin_INCLUDE_DIRS}
)


#catkin_install_python(PROGRAMS scripts/Principal.py
#  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
#)


