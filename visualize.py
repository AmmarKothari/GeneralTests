#!/usr/bin/env python

# external
from pydy.viz.shapes import Cylinder, Sphere
from pydy.viz.scene import Scene
from pydy.viz.visualization_frame import VisualizationFrame

# local
from derive import I, O, links, q, u
from simulate import param_syms, state_trajectories, param_vals
from simulate import link_length, link_radius

import pdb
# A cylinder will be attached to each link and a sphere to each bob for the
# visualization.

viz_frames = []

for i, link in enumerate(links):

    link_shape = Cylinder(name='cylinder{}'.format(i),
                          radius=link_radius,
                          length=link_length,
                          color='red')

    viz_frames.append(VisualizationFrame('link_frame{}'.format(i), link,
                                         link_shape))

# Now the visualization frames can be passed in to create a scene.
scene = Scene(I, O, *viz_frames)

# Provide the data to compute the trajectories of the visualization frames.
scene.constants = dict(zip(param_syms, param_vals))
scene.states_symbols = q + u
scene.states_trajectories = state_trajectories
pdb.set_trace()
scene.display()
