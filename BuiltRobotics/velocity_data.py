#extracts velocity data from a >> .txt bash dump



FN = "/home/ammar/built_ws/velocity_data_2.txt"

dx = dy = dz = 0.0
v = []
with open(FN, 'r') as f:
	for line in f:
		if '---' in line:
			cur_v = np.linalg.norm([dx, dy, dz])
			if abs(cur_v) > 0.01:
				v.append(cur_v)
			continue # line break
		else:
			if 'x' in line:
				dx = float(line.split(':')[1])
			if 'y' in line:
				dy = float(line.split(':')[1])
			if 'z' in line:
				dz = float(line.split(':')[1])

pdb.set_trace()
plt.plot(v, 'ro-')

plt.show()
