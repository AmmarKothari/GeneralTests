# Need this to ensure that the test makes sense given current params
import math
import time

from pybuilt.integration_tests.actions import navigate_action_test_helper, navigate_action_sim_test_fixture
from pybuilt.planning import region_factory
from pybuilt.util import param_helper, bnode
from pybuilt.vehicle_clients import vehicle_client
from pybuilt.util.btf import btf

# vehicle_blaunch_files = ['dorothy_sim',  'vehicle_test']
vehicle_blaunch_files = ['billy_sim', 'vehicle_test']
params_dict = param_helper.get_param_dict_from_blaunch(vehicle_blaunch_files)
track_front_base_link_x_offset = params_dict['track_front_base_link_x_offset']
base_link_to_track_edge_y_offset = params_dict['base_link_to_track_edge_y_offset']
large_car_shape_padding = params_dict['car_shapes']['large']['x_padding']

obs_side_length = 10.0

footprint_diagonal_length = math.hypot(track_front_base_link_x_offset + large_car_shape_padding,
                                       base_link_to_track_edge_y_offset + large_car_shape_padding)

bnode.init('test_objects', publish_shutdown=False, check_heartbeat=False)
btf.init()

vehicle = vehicle_client.VehicleFactory.get_vehicle()
base_link = vehicle.base_link()

obs_point_1 = [obs_side_length / 2.0 + footprint_diagonal_length + 0.1, 0.0, 0.0]
obs_point_2 = [-1 * obs_point_1[0], obs_point_1[1], obs_point_1[2]]
obstacles = [
    navigate_action_test_helper.square_obstacle(obs_point.xyz, obs_side_length) for obs_point in [base_link.offset(xyz=obs_point_1), base_link.offset(xyz=obs_point_2)]
]
obstacle_type = region_factory.RegionType.NOPLAN






navigate_action_sim_test_fixture._add_obstacles(obstacle_type, obstacles)
print('Finished Adding obstacles at {}'.format(time.time()))
