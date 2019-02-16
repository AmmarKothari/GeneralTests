from built.msg import NavigateGoal, ProfileState
from pybuilt.actions.profile import Profile
from pybuilt.util.bparam import BParam
from pybuilt.util.bpose import BPose
from pybuilt.util import bviz, helpers
import pdb

gparam = lambda x: BParam.instance().get(x)


error_rough = gparam('/bulldoze/forward_prof_error_rough')
error_fine = gparam('/bulldoze/forward_prof_error_fine')


bps = [BPose(xyz=[0,0,10], frame_id='ws_center'), BPose(xyz=[10,0,0], frame_id='ws_center')]
width = 3.0

prof_state = ProfileState(
            cut_points=[bp.ros_pose_stamped() for bp in bps],
            cutting_edge_width=width,
            max_cutting_angle_degs=90,  # TODO fix this profile bullshit
            error_rough=error_rough,
            error_fine=error_fine)

prof = Profile(prof_state, 'map', should_smooth_cut_pts=True)

helpers.init_node('test_profile')

while True:
	pdb.set_trace()
	rospy.spin()