addpath(fullfile('../../', 'ROB541_GeometricMecahnics','Random', 'GeoOps2D'));


% setup!
f = figure(1);
clf(f);
ax = axes(f);

rev_axis = [0,0,1];
rev_axis_neg = [0,0,-1];

base = link_gripper('base', false, rev_axis, [0.5,0,0], 'g', [0,0,0]);
left_proximal = link_gripper('left_prox', 'base', rev_axis_neg, [2,0,pi/4], 'k', [1,0,0]);
left_distal = link_gripper('left_dist', 'left_prox', rev_axis_neg, [2,0,-pi/8], 'y', [1,0,0]);
right_proximal = link_gripper('right_prox', 'base', rev_axis, [2,0,0], 'b', [1,0,0]);
right_distal = link_gripper('right_dist', 'right_prox', rev_axis, [2,0,pi/8], 'r', [1,0,0]);

obj = grasp_object('rectangle');
obj = obj.setDims([0.5,0.5]);
obj = obj.setLocation([5,2]);



g = gripper([base, left_proximal, left_distal, right_proximal, right_distal], 1);
g = g.calc_poses([0, -pi/8, 0, 0, 0]);
g.draw(ax);
obj.draw(ax);
axis equal

contact_points = [obj.center(1), obj.center(2)+obj.dims(2);
                obj.center(1), obj.center(2)-obj.dims(2)];
hold on
plot(ax, contact_points(:,1), contact_points(:,2), 'o')
hold off

% solve for angles to touch end to contact points
% minimize squared error
end_pts = g.endPoints();
alphas = g.invKin(contact_points);
start_alphas = g.get_alphas();
P = Planner(g);
alpha_path = P.linearAlphaPath(start_alphas, alphas, 100);
xy_path = P.xy_path(alpha_path);
P = P.costMap();
for i = 1:length(alpha_path)
    cla
    contour(P.x_range, P.y_range, P.cost_map)
    g = g.calc_poses(alpha_path(i,:));
    g.draw(ax);
    obj.draw(ax);
    axis equal
    pause(0.01);
end




