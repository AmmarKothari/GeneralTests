
from stl import mesh
from pybuilt.util import helpers, param_helper
from pybuilt.util.geom import mesh_utils
from pybuilt.util.bparam import BParam
from pybuilt.perception.maps.terrain_map import TerrainMap
import glob
import pdb
from pybuilt.script import commands
from pybuilt.perception.util.terrain_map_publisher_pool import save_terrain_map
import multiprocessing
import os
import datetime
import scipy.interpolate

import pdb

def get_cell_indices(xyzs, resolution, min_xy):
	return np.around((xyzs[:, :2] - min_xy[:2]) / resolution).astype(np.int32)

def get_cell_coords(resolution, dims, min_xy):
    x_ind, y_ind = np.indices(dims)
    map_coords_x = x_ind * resolution + min_xyz[0]
    map_coords_y = y_ind * resolution + min_xyz[1]
    return np.stack((map_coords_x, map_coords_y), axis=2)

machine = 'local'
job_yaml = 'river_islands.yaml'
system_yaml = 'system.yaml'

# start ros and other things
# commands.roscore(machine, multiprocessing.Event())
param_helper.load_and_set_params_from_files([job_yaml, system_yaml])


m = mesh_utils.load_raw_site_mesh()
max_xyz, min_xyz = mesh_utils.mesh_bounds_xyz(m)


resolution = BParam.instance().get('terrain_map_publisher/resolution')

# create a grid
steps = np.ceil((max_xyz - min_xyz)/resolution).astype(int)

estimated_heights = np.zeros(steps[0:2])
estimated_variances = np.zeros(steps[0:2])
save_times = np.zeros(steps[0:2])

terrain_map_file_template = BParam.instance().get('asset_tmp_dir') + 'terrain_map_publisher_' + BParam.instance().get('job') + '_{}' + '.npz'
terrain_map_files = glob.glob(terrain_map_file_template.format('*'))


for fn in terrain_map_files:
    data = np.load(fn)
    save_time = data['time']
    grid_indices = get_cell_indices(data['coords'], resolution, min_xyz[:2])
    for ind, coords_height_var in zip(grid_indices, data['coords']):
        # check if within bounds of current terrain map
        if ind[0] < 0 or steps[0] <= ind[0] or ind[1] < 0 or steps[1] <= ind[1]:
            continue
        # check if more recent than current measurement -- if not continue
        elif save_times[ind[0], ind[1]] >= save_time:
            continue
        else:
            estimated_heights[ind[0], ind[1]] = coords_height_var[2]
            estimated_variances[ind[0], ind[1]] = coords_height_var[3]
            save_times[ind[0], ind[1]] = save_time

# plt.imshow(estimated_heights)
# plt.show()
pdb.set_trace()
# move all the old files somewhere
old_terrain_map_full_folder_path = BParam.instance().get('asset_tmp_dir') + OLD_TERRAIN_MAP_FOLDER
if not os.path.exists(old_terrain_map_full_folder_path):
	os.makedirs(old_terrain_map_full_folder_path)
for fn in terrain_map_files:
	new_fn = fn.replace(BParam.instance().get('asset_tmp_dir'), old_terrain_map_full_folder_path)
	os.rename(fn, new_fn)


new_terrain_map_fn = terrain_map_file_template.format('site_wide_{}'.format(datetime.datetime.today().strftime('%Y_%m_%d')))
coords = get_cell_coords(resolution, steps[0:2], min_xyz[:2])
save_terrain_map_pool_target(coords, estimated_heights, estimated_variances, 0.0, steps[:2], (min_xyz, max_xyz), new_terrain_map_fn)
	# os.remove(fn)

# someway to run this on Ricardo

print("ROS is still running on {}.  Kill it if necessary".format(machine))
