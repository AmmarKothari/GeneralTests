#!/usr/bin/env python
import numpy as np
import unittest
import pytest

from pybuilt.nodes import action_manager
from pybuilt.nodes.action_manager import ros_action_service
from pybuilt.util import bnode
from pybuilt.util.action import action_client
from pybuilt.integration_tests.test_tools import test_machine_utils
from pybuilt.util.btf import btf
from built import msg
from pybuilt.actions.workspaces.lane import Lane as lane_class
from pybuilt.integration_tests.test_tools import blaunch_test_env


# class BulldozeActionSimTest(unittest.TestCase):
#
#     def setUp(self):
#         blaunch_test_env.TestEnvController.request_environment(blaunch_files=['rick_sim', 'vehicle_test'])
#
#     def tearDown(self):
#         blaunch_test_env.TestEnvController.shutdown()
#
#     @pytest.mark.large
#     @pytest.mark.ros_stack
#     def test_bulldoze(self):
#         blaunch_test_env.TestEnvController.assert_no_nodes_dead()
btf.init()
bnode.init('debug_bulldoze_action_sim', publish_shutdown=False)



bulldoze_goal_cls, bulldoze_result_cls, bulldoze_status_cls, bulldoze_server_topic = action_manager.ACTION_DICT['bulldoze']
is_bulldoze_up = ros_action_service.wait_for_action_available('bulldoze', service_timeout=30.0, action_server_timeout=90.0)
bulldoze_client = action_client.BuiltActionClient(bulldoze_server_topic, bulldoze_goal_cls, bulldoze_result_cls, bulldoze_status_cls)

current_bpose = btf.lookup_transform(source='map', target='base_link', wait=20)
navigate_goal_bpose = current_bpose.offset(xyz=(10.0, 10.0, 0.0), rpy=(0.0, 0.0, 0.0))



navigate_goal = msg.NavigateGoal(
    target_pose_s=navigate_goal_bpose.ros_pose_stamped(),
    mode=msg.NavigateGoal.MODE_PRECISE_FORWARD,
    speed=0.5,
    orientation_tol=0.1)

# Generate a lane from navigate goal
push_lane = lane_class([navigate_goal_bpose.offset(xyz=(x, 0.0, 0.0)) for x in np.linspace(0, 10, 6)], width=0.5)

pushing_lane = push_lane.to_ros_msg()

pushing_effector_msg = msg.PushingEffectorGoal(
    lineup_nav_goal=navigate_goal,
    end_lane_nav_bp=navigate_goal_bpose.offset(xyz=(10, 0, 0)).ros_pose_stamped(),
    push_speed=1.2,
    slowdown_speed=0.4,
    accuracy=msg.PushingEffectorGoal.ACCURACY_ROUGH,
    finish_on_nav_done=False,
    pushing_lane=pushing_lane,
    final_lane=pushing_lane)

goal = bulldoze_goal_cls(pushing_effector_msg=pushing_effector_msg, cutting_yaw=1.0)

test_machine_utils.go_to_autonomous_mode(timeout=180)

reqs = bulldoze_client.send_new_goal(goal)

result = reqs.wait_for_result(timeout=300.0)


import pdb
pdb.set_trace()