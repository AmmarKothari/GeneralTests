import rosbag
import pdb
import sensor_msgs.point_cloud2 as pc2
from sys import getsizeof
import time


def showMsgInfo(gen, name):
	# pdb.set_trace()
	while True:
		try:
			_, msg, _ = gen.next()
			break
		except:
			continue
	pointcloud = np.array(list(pc2.read_points(msg)))
	print("First Line of {}: {}".format(name, pointcloud[0]))
	print("Size of message: {}".format(getsizeof(msg)))
	print("Size of pointcloud: {}".format(pointcloud.nbytes))
	print("Frame of Cloud: {}").format(msg.header.frame_id)
	return pointcloud


rosbag_fn_rick = "2018-09-19-14-44-29.bag"
# rosbag_fn_sim = "2018-09-19-15-27-28.bag"
# rosbag_fn_sim = "2018-09-19-15-53-04.bag"
# rosbag_fn_sim = "2018-09-19-16-01-57.bag"
# rosbag_fn_sim = "2018-09-19-16-13-45.bag"
# rosbag_fn_sim = "2018-09-19-16-27-37.bag"
# rosbag_fn_sim = "2018-09-19-16-30-16.bag"
rosbag_fn_sim = "2018-09-19-16-42-06.bag"
# rosbag_fn_sim = "sim_ri_test_2018-09-20-10-26-10.bag"

recorded_bag_rick = rosbag.Bag(rosbag_fn_rick, 'r')
recorded_bag_sim = rosbag.Bag(rosbag_fn_sim, 'r')
rick_pc2_gen = recorded_bag_rick.read_messages(topics = '/terrain_map/pc2')
sim_pc2_gen = recorded_bag_sim.read_messages(topics = '/terrain_map/pc2')
time.sleep(1)
for i in range(100):
	sim_pc = showMsgInfo(sim_pc2_gen, "Sim")
	rick_pc = showMsgInfo(rick_pc2_gen, "Rick")
	pdb.set_trace()

