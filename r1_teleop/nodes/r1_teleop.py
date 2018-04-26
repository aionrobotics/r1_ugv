#!/usr/bin/env python

"""
Teleop node for R1 rover in simulation using Joy with Xbox 360 wired controller.
Ref: 
	https://andrewdai.co/xbox-controller-ros.html#rosjoy
	https://github.com/turtlebot/turtlebot/blob/kinetic/turtlebot_teleop/scripts/turtlebot_teleop_key

See http://wiki.ros.org/joy for button mapping.
"""

import rospy
import numpy as np
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Joy

LINEAR_SPEED = 0.5
ANGULAR_SPEED = 0.5
start_msg = """
Control Your Rover!
---------------------------
Moving around:

            RT : drive forward
            LT : drive backward
    Left stick : steer
             A : decrease max linear speed by 10%
             B : increase max linear speed by 10%
             X : decrease max angular speed by 10%
             Y : increase max angular speed by 10%
         Start : reset speeds
 anything else : stop smoothly

CTRL-C to quit
"""

class Teleop(object):

	def __init__(self):

		print(start_msg)

		self.pub = rospy.Publisher('cmd_vel_mux/input/teleop', Twist, queue_size=5)
		self.sub = rospy.Subscriber('joy', Joy, self.callback)
		self.linear_speed = LINEAR_SPEED
		self.angular_speed = ANGULAR_SPEED
		self.button_state = np.zeros(11, dtype=bool)
		
		self.target_linear = 0
		self.target_angular = 0
		self.cmd_linear = 0
		self.cmd_angular = 0

		self.controller_update_rate = 50  # Hz
		self.linear_accel = 1.0 / self.controller_update_rate  
		self.angular_accel = 5.0 / self.controller_update_rate

	def update_speed(self, buttons):

		old_state = self.button_state
		self.button_state = np.array(buttons, dtype=bool)
		pressed = (old_state == False) & (self.button_state == True)

		if pressed[0] == True:  # A
			self.linear_speed *= 0.90
			rospy.loginfo('Reducing linear speed by 10%% to %1.2f', self.linear_speed)

		if pressed[1] == True:  # B
			self.linear_speed *= 1.10
			rospy.loginfo('Increasing linear speed by 10%% to %1.2f', self.linear_speed)

		if pressed[2] == True:  # X
			self.angular_speed *= 0.90
			rospy.loginfo('Reducing angular speed by 10%% to %1.2f', self.angular_speed)

		if pressed[3] == True:  # Y
			self.angular_speed *= 1.10
			rospy.loginfo('Increasing angular speed by 10%% to %1.2f', self.angular_speed)

		if pressed[7] == True:  # Start
			self.linear_speed = LINEAR_SPEED
			self.angular_speed = ANGULAR_SPEED
			rospy.loginfo('Resetting linear and angular speeds to (%1.2f, %1.2f)', 
				self.linear_speed, self.angular_speed)

		old_state = self.button_state


	def callback(self, data):

		# update speeds by registering button presses
		self.update_speed(data.buttons)

		# forward/backward linear command with RT/LT
		rt = (1.0 - data.axes[5]) * 0.5  # remap to [0, 1]
		lt = (1.0 - data.axes[2]) * 0.5  # remap to [0, 1]

		# enforce 'nothing' if both triggers are held
		if rt > 0.0 and lt > 0.0:
			self.target_linear = 0.0
		elif rt > 0.0:
			self.target_linear = rt * self.linear_speed
		else:
			self.target_linear = -lt * self.linear_speed
		
		# turning radius with left/right on left stick 
		angular_dir = 1 if np.sign(self.cmd_linear) == 0 else np.sign(self.cmd_linear)
		self.target_angular = data.axes[0] * self.angular_speed * angular_dir

if __name__ == '__main__':

	print(__doc__)

	rospy.init_node('r1_teleop')
	teleop = Teleop()
	rate = rospy.Rate(teleop.controller_update_rate)  # Hz

	while not rospy.is_shutdown():

		msg = Twist()

		# smooth out the commands sent to the controller
		if teleop.target_linear > teleop.cmd_linear:
			teleop.cmd_linear = min(teleop.target_linear, teleop.cmd_linear + teleop.linear_accel)
		elif teleop.target_linear < teleop.cmd_linear:
			teleop.cmd_linear = max(teleop.target_linear, teleop.cmd_linear - teleop.linear_accel)
		else:
			teleop.cmd_linear = teleop.target_linear

		if teleop.target_angular > teleop.cmd_angular:
			teleop.cmd_angular = min(teleop.target_angular, teleop.cmd_angular + teleop.angular_accel)
		elif teleop.target_angular < teleop.cmd_angular:
			teleop.cmd_angular = max(teleop.target_angular, teleop.cmd_angular - teleop.angular_accel)
		else:
			teleop.cmd_angular = teleop.target_angular

		# populate the message and publish
		rospy.logdebug('Linear velocity: %1.2f --> %1.2f', teleop.cmd_linear, teleop.target_linear)
		rospy.logdebug('Angular velocity: %1.2f --> %1.2f', teleop.cmd_angular, teleop.target_angular)
		msg.linear.x = teleop.cmd_linear
		msg.angular.z = teleop.cmd_angular
		teleop.pub.publish(msg)

		# sleep for a bit
		rate.sleep()
