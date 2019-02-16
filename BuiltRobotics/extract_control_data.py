import rosbag
from built.msg import D6ControlStatus
import os

fn = '~/Desktop/control_data_hot_1.bag'

bag = rosbag.Bag(os.path.expanduser(fn), 'r')

control_data = []
odom_data = []
yaw_track_data = []
linear_track_data = []
for topic, msg, t in bag.read_messages():
	if 'Control' in msg._type:
		row = [t.to_sec(), msg.throttle, msg.brake, msg.decel]
		control_data.append(row)
	elif 'Odom' in msg._type:
		row = [t.to_sec(), np.linalg.norm([msg.twist.twist.linear.x, msg.twist.twist.linear.y, msg.twist.twist.linear.z])]
		odom_data.append(row)
	elif 'yaw' in topic:
		row = [t.to_sec(), msg.data]
		yaw_track_data.append(row)
	elif 'linear' in topic:
		row = [t.to_sec(), msg.data]
		linear_track_data.append(row)
	else:
		pdb.set_trace()

control_data = np.array(control_data)
odom_data = np.array(odom_data)
yaw_track_data = np.array(yaw_track_data)
linear_track_data = np.array(linear_track_data)

m = 4 # rows
n = 1 # cols

pdb.set_trace()
# plt.plot(data[:,0], data[:,1], 'rx')
plt.subplot(m,n,1)
plt.plot(control_data[:,0], control_data[:,2], 'bx')
plt.subplot(m,n,2)
plt.plot(control_data[:,0], control_data[:,3], 'cx')
plt.subplot(m,n,3)
plt.plot(odom_data[:,0], odom_data[:,1], 'yo')
plt.subplot(m,n,4)
plt.plot(linear_track_data[:,0], linear_track_data[:,1], 'g:')

plt.show()
pdb.set_trace()