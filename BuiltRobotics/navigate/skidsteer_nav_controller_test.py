import pytest

from pybuilt.controls.navigation import nav_path, skidsteer_nav_controller
from pybuilt.test.test_tools import mocks
from pybuilt.util import bpose

MOCKUP_PARAM_DICT = {
    'nav_controller_no_turn_in_place': {
        'kp_speed': 0.015,
        'kp_yaw': 0.04,
        'max_demand_speed': 1.8,
        'min_demand_speed': 0.3,
        'max_lin_js_def': 1.0,
        'min_lin_js_def': 0.3,
        'min_lin_js_deflection_while_turning': 0.5,
        'min_yaw_js_deflection_to_be_turning': 0.25,
        'near_aim_wp_limit_turn_cutoff_dist': 0.5,
        'near_aim_wp_turn_max_deflection': 0.001
    }
}


# -------------------------------------------------------------
# Test Fixtures
# -------------------------------------------------------------
@pytest.fixture
def param_client():
    return mocks.MockParamClient(MOCKUP_PARAM_DICT)


@pytest.fixture("function")
def skidsteer_controller(param_client):
    return skidsteer_nav_controller.SkidsteerNavController(param_client.get('nav_controller_no_turn_in_place'))


# -------------------------------------------------------------
# Tests
# -------------------------------------------------------------
def test_publish_in_nav_to_bp(param_client):
    with mocks.PublisherMockContext() as publisher_mock:
        # Need to initialize controller here to capture publishers
        skidsteer_controller = skidsteer_nav_controller.SkidsteerNavController(
            param_client.get('nav_controller_no_turn_in_place'))
        # Manually update odometry
        skidsteer_controller.update_odometry(bpose.BPose(), 0.0)

        skidsteer_controller.nav_to_bp(bpose.BPose(xyz=(1.0, 0.0, 0.0)), 1.0, nav_path.Direction.FORWARD)
        yaw_js_pub = publisher_mock.publisher_mocks['/machine_hw/tracks/yaw']
        linear_js_pub = publisher_mock.publisher_mocks['/machine_hw/tracks/linear']
    yaw_js_pub.publish.assert_called_once()
    linear_js_pub.publish.assert_called_once()


# -------------------------------------------------------------
# Plotting Tests
# -------------------------------------------------------------
@pytest.mark.skip
def test_estimate_target_js_deflection(skidsteer_controller):
    import matplotlib.pyplot as plt
    import numpy as np
    lin_js_deflection = []
    speeds = np.arange(0.0, 2.0, 0.1)
    for speed in speeds:
        js_deflection = skidsteer_controller._estimate_target_js_deflection(speed)
        lin_js_deflection.append(js_deflection)

    plt.plot(speeds, lin_js_deflection, 'rx-')
    plt.title('JS deflection vs speed')
    plt.xlabel('Target Speeds (m/s)')
    plt.ylabel('Mapped JS Deflections')
    min_js = skidsteer_controller._param_client.get('/navigate/min_lin_js_def')
    max_js = skidsteer_controller._param_client.get('/navigate/max_lin_js_def')
    min_demand_speed = skidsteer_controller._param_client.get('/navigate/min_demand_speed')
    max_demand_speed = skidsteer_controller._param_client.get('/navigate/max_demand_speed')

    out = plt.gca()
    out.axhline(y=min_js, label='Min JS Deflection', color='g')
    out.axhline(y=max_js, label='Max JS Deflection', color='r')
    out.axvline(x=min_demand_speed, label='Min Demand Speed', color='b')
    out.axvline(x=max_demand_speed, label='Max Demand Speed', color='k')
    plt.legend()
    plt.show()


@pytest.mark.skip
def test_linear_deflection(skidsteer_controller):
    import matplotlib.pyplot as plt
    import numpy as np
    speeds = np.arange(-2.0, 2.0, 0.1)

    data = {}
    for current_speed in np.arange(-2.0, 2.0, 0.5):
        skidsteer_controller.cur_speed = current_speed
        lin_js_deflection = []
        for desired_speed in speeds:
            direction = nav_path.Direction.FORWARD if desired_speed >= 0 else nav_path.Direction.BACKWARD
            js_deflection = skidsteer_controller._linear_deflection(desired_speed, direction)
            lin_js_deflection.append(js_deflection)
        data[current_speed] = lin_js_deflection

    for current_speed, js_deflections in data.items():
        plt.plot(speeds, js_deflections, label='{:.1f}'.format(current_speed))
        plt.title('JS deflection vs speed')
        plt.xlabel('Target Speeds (m/s)')
        plt.ylabel('Mapped JS Deflections')
    plt.legend(title='Current vehicle velocity')

    plt.show()
    # import pdb
    # pdb.set_trace()
