addpath(fullfile('../../../', 'ROB541_GeometricMecahnics','Random', 'GeoOps2D'));

rev_axis = [0,0,1];
rev_axis_neg = [0,0,-1];

base = link_gripper('base', false, rev_axis, [0.5,0,0], 'g', [0,0,0]);
left_proximal = link_gripper('left_prox', 'base', rev_axis_neg, [2,0,pi/4], 'k', [1,0,0]);
left_distal = link_gripper('left_dist', 'left_prox', rev_axis_neg, [2,0,-pi/8], 'y', [1,0,0]);

g = gripper([base, left_proximal, left_distal]);

% Draw Gripper
g.draw(ax);
obj.draw(ax);
axis equal
