


import scipy.interpolate

import pdb

data = np.load('/built_tmp/old_terrain_maps/terrain_map_publisher_river_islands_3e7f61a01cc3bc5069477952c736c5d1a346c6ca_2fa09cfcb2340aac2bc3b672349e589b153e7e2c_15.npz')


out_interp = scipy.interpolate.interp2d(data['coords'][:,0], data['coords'][:,1], data['coords'][:,2], kind='linear', fill_value = 0)


pdb.set_trace()