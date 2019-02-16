
import datetime
import os
import copy

fn = os.path.expanduser('~/.ros/log/5edfc9fa-dc9f-11e8-b051-34e12dd93960/bstdout.log')


text_dict = {'Profile within tolerance of Terrain map': [],
			'Effector within tolerance of Profile': [],
			'Effector within tolerance of Terrain map': []}

t_start = None

text_ids = text_dict.keys()
with open(fn, 'rb') as f:
	for line in f.readlines():
		if 'PushingEffectorAbstractServer' in line:
			for i,id in enumerate(text_ids):
				if id in line:
					time = datetime.datetime.strptime(line.split('|')[1].split()[1], '%H:%M:%S.%f')
					val = float(line.split(':')[-1].split(' ')[1])
					if t_start is None:
						t_start = copy.deepcopy(time)
					t_delta = (time - t_start).total_seconds()
					text_dict[id].append([t_delta, val])
					break


for i,k in enumerate(text_dict.keys()):
	text_dict[k] = np.array(text_dict[k])

upper_lim = 0.5
lower_lim = -0.5

color_list = []
for i in range(len(text_dict[text_dict.keys()[0]])):
	flag = 'r'
	if text_dict[text_ids[0]][i][1] < upper_lim and \
		text_dict[text_ids[1]][i][1] < upper_lim and \
		lower_lim < text_dict[text_ids[2]][i][1] < upper_lim:
		# pdb.set_trace()
		# if abs(text_dict[k][i][1]) > 0.1:
			flag = 'g'
	color_list.append(flag)

color_list = np.array(color_list)
# color_list = np.expand_dims(color_list, axis=1)
# pdb.set_trace()
m = 3
n = 1
for i,k in enumerate(text_dict.keys()):
	text_dict[k] = np.array(text_dict[k])
	data = text_dict[k]
	plt.subplot(m,n,i+1)
	# plt.plot(data[:,0], data[:,1], 'rx', color=color_list)
	plt.scatter(data[:,0], data[:,1], c=color_list)
	# plt.plot(data[color_list,0], data[color_list,1], 'rx')
	plt.plot(data[[0,-1],0], [upper_lim, upper_lim], 'k-')
	if i == 2:
		plt.plot(data[[0,-1],0], [lower_lim, lower_lim], 'k-')

plt.show()

pdb.set_trace()