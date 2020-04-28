import math

import pytest
import pantograph_internet_formula as pf

import pdb
import numpy as np


@pytest.fixture
def pantograph_config():
    L1 = 1
    L2 = 2
    L4 = 1
    L3 = 2

    L5 = 1.0
    theta_m = 0.0
    return pf.PantographConfig(theta_m, L5, L1, L2, L4, L3)


@pytest.fixture
def pantograph(pantograph_config):
    pantograph = pf.Pantograph(pantograph_config)
    p1 = [0.0, 0.0]
    pantograph.set_body_pos(*p1)
    return pantograph


@pytest.fixture
def pantograph_offset(pantograph):
    pantograph.set_body_pos(20.0, 20.0)
    return pantograph


@pytest.fixture
def pantograph_body(pantograph_config):
    pantograph = pf.EEFixedPantograph(pantograph_config)
    p1 = [0.0, 0.0]
    pantograph.set_foot_pos(*p1)
    return pantograph


def test_forward_foot_moving(pantograph):
    end_point = pantograph.forward([math.pi / 2, math.pi / 2])
    assert end_point[0] == 0.5
    assert np.isclose(end_point[1], 1 + math.sqrt(2**2 - 0.5**2))
    end_point = pantograph.forward([math.pi, 0.0])
    assert end_point[0] == 0.5
    assert np.isclose(end_point[1], math.sqrt(2 ** 2 - 1.5 ** 2))
    end_point = pantograph.forward([3 * math.pi / 2, 3 * math.pi / 2])
    assert np.isclose(end_point[0], 0.5)
    assert np.isclose(end_point[1], math.sqrt(2**2 - 0.5**2)-1)


def test_forward_foot_moving_offset(pantograph_offset):
    end_point = pantograph_offset.forward([math.pi / 2, math.pi / 2])
    assert end_point[0] == (20 + 0.5)
    assert np.isclose(end_point[1], 20 + 1 + math.sqrt(2**2 - 0.5**2))


def test_inverse_foot_moving(pantograph):
    end_point = pantograph.forward(pantograph.inverse(0, 2))
    assert np.isclose(end_point[0], 0) and np.isclose(end_point[1], 2)


def test_inverse_foot_moving_offset(pantograph_offset):
    end_point = pantograph_offset.forward(pantograph_offset.inverse(20, 22))
    assert np.isclose(end_point[0], 20) and np.isclose(end_point[1], 22)


def test_forward_body_moving(pantograph_body):
    # First links vertically down
    body_point = pantograph_body.forward([math.pi / 2, math.pi / 2])
    assert np.isclose(body_point[0], 0.5)
    assert np.isclose(body_point[1], 1 + math.sqrt(2**2 - 0.5**2))
    # import pdb; pdb.set_trace()
    # First links horizontally out - ambiguous because could be above or below
    body_point = pantograph_body.forward([math.pi, 0.0])
    assert np.isclose(body_point[0], 0.5)
    assert np.isclose(body_point[1], math.sqrt(2 ** 2 - 1.5 ** 2))
    # First links vertically up
    body_point = pantograph_body.forward([3 * math.pi / 2, 3 * math.pi / 2])
    assert np.isclose(body_point[0], 0.5)
    assert np.isclose(body_point[1], math.sqrt(2**2 - 0.5**2) - 1)


def test_inverse_body_moving(pantograph_body):
    body_point = pantograph_body.forward(pantograph_body.inverse(0, 2))
    assert np.isclose(body_point[0], 0) and np.isclose(body_point[1], 2)

# def test_inverse_body_pos(pantograph):
#     # TODO: Figure out how to make this work with the current structure!
#     joints = pantograph.inverse_body_pos(0, 1, [0, 3])
#     pdb.set_trace()
