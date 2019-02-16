
# Original Pad at the office
P1 = np.array([-23, 4, -0.45])
P2 = np.array([-29, 4, -0.45])
P3 = np.array([-24, 10, -0.45])
P4 = np.array([-17, 10, -0.45])

# Second Pad at the office
P5 = np.array([-2, 15, -0.45])
P6 = np.array([-2, 10, -0.45])
P7 = np.array([-10, 15, -0.45])
P8 = np.array([-10, 10, -0.45])


# rosrun tf tf_echo ws_center map
translation = -1*np.array([-1833736.000, -639874.000, 0.000])

for P in (P1, P2, P3, P4, P5, P6, P7, P8):
	str1 = ', '.join(['%.2f' % num for num in P])
	str2 = ', '.join(['%.2f' % num for num in P + translation])
	print('{} --> {}'.format(str1, str2))

