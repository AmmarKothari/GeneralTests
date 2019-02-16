#!/usr/bin/python
from __future__ import division

import math

import numpy as np
import sys

import rospy
import rosbag
import csv
from std_msgs.msg import Float32, Bool
from nav_msgs.msg import Odometry

from pybuilt.hardware.util.trimble_gps import TrimbleInterface
from pybuilt.hardware.sim.trimble_gps import SimTrimbleInterface
from pybuilt.hardware.util.gps_message import wrap_trimble_msg
from pybuilt.util import btf, bviz, helpers, unit_conversion_helper as uch
from pybuilt.util.bpose import BPose
from pybuilt.util.built_super import BuiltSuper
from pybuilt.util.color import Color
from pybuilt.util.gps import gps_transformations as gps_t
from pybuilt.vehicle_clients.vehicle_client import VehicleFactory
from built.msg._D6Imu import D6Imu

import pdb


IMU_TOPIC = '/effector/imu'



# @ros_numpy.converts_to_numpy(D6Imu)
# def convert(msg):
#     return np.array([1,2,3])




class RecordIMUData(BuiltSuper):
    """abstract clas for recording IMU data."""

    def __init__(self, message_fn):
        super(RecordIMUData, self).__init__()
        self.message_fn = message_fn
        rospy.Subscriber('/effector/imu', D6Imu, self.receive_imu, queue_size=1, tcp_nodelay=True)

    def receive_imu(self, msg):
        pass

    def close(self):
        pass


class RecordIMUData_text(RecordIMUData):
    """records all the incoming IMU messages to a text file."""

    def receive_imu(self, msg):
        with open(message_fn + ".txt", 'a') as message_file:
            message_file.write(msg.__str__() + "\n")


class RecordIMUData_bag(RecordIMUData):
    """records all the incoming IMU data to a bag file."""

    def __init__(self, message_fn):
        super(RecordIMUData_bag, self).__init__(message_fn)
        self.bag = rosbag.Bag(self.message_fn +'.bag', 'w')

    def receive_imu(self, msg):
        self.bag.write(IMU_TOPIC, msg)

    def close(self):
        if self.bag is not None:
            self.bag.close()


class ExtractIMUData():
    """extracts the imu data from the recorded messages as a set of csv files."""

    def __init__(self, message_fn):
        self.message_fn = message_fn
        self.extract_fn = message_fn + "_extracted"


class ExtractIMUData_Text(ExtractIMUData):
    """extracts the imu data from a text file and outputs to csv"""

    def extract(self):
        with open(self.extract_fn + ".txt", 'wb') as extract_file:
            for message in self.get_next_msg():
                pdb.set_trace()

    def get_next_msg(self):
        """Extracts each message.

        :return:
        """

        message_str = None
        with open(self.message_fn + ".txt", 'rb') as message_file:
            for line in message_file:
                if "header:" in line:
                    if message_str is not None:
                        yield message_str
                    message_str = line
                else:
                    message_str += line

class ExtractIMUData_Bag(ExtractIMUData):
    """extracts imu data from a bag file and outputs to a csv"""

    def extract(self):
        self.bag = rosbag.Bag(self.message_fn + '.bag')
        with open(self.extract_fn +".csv", 'wb') as imu_csv:
            imu_csv_writer = csv.writer(imu_csv, delimiter=',')
            for topic, msg, t in self.bag.read_messages(topics = IMU_TOPIC):
                # pdb.set_trace()
                row = []
                row.append(str(msg.cab.header.stamp))
                for individual_imu_msg in (msg.cab, msg.arm, msg.blade, msg.ripper):
                    row.extend([individual_imu_msg.orientation.x, individual_imu_msg.orientation.y, individual_imu_msg.orientation.z, individual_imu_msg.orientation.w])
                    row.extend([individual_imu_msg.angular_velocity.x, individual_imu_msg.angular_velocity.y, individual_imu_msg.angular_velocity.z])
                    row.extend([individual_imu_msg.linear_acceleration.x, individual_imu_msg.linear_acceleration.y, individual_imu_msg.linear_acceleration.z])
                row.append(msg.yaw_angle_degs)
                imu_csv_writer.writerow(row)



if __name__ == '__main__':
    message_fn = sys.argv[1]  # filename to save the messages without any extension
    helpers.init_node('record_imu')
    node = RecordIMUData_bag(message_fn)
    print("in main")
    while not rospy.is_shutdown():
        continue
    node.close()
    extractor = ExtractIMUData_Bag(node.message_fn)
    extractor.extract()
