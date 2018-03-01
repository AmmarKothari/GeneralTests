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
obj = obj.setBoundary();

g = gripper([base, left_proximal, left_distal, right_proximal, right_distal], 1);
g = g.calc_poses([0, -pi/8, 0, 0, 0]);
g.draw(ax);
obj.draw(ax);
axis equal

Q_INPUTS = 5;
TRAJ_NOISE = 1e-2; % noise scaled to joint range in trajectory in STOMP
NOISE_COOLING = 0.99;
TRAJ_STEPS = 100;
OBJ_NOISE = 0.05;
BLUR_FILTER_SIZE = 5;
NOISEY_TRAJS = 5;
TRAJ_DT = 0.01;
STOMP_STOP_COND = 0.01;

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
M = Map();
M = M.addObject(obj);
M = M.limits();
% M = M.costMap();
noise_map = M.noiseCostMap(10, OBJ_NOISE);
dist_map  = M.addDistMap(contact_points);
blur_map  = M.blurCostMap(BLUR_FILTER_SIZE, dist_map);
% P = P.setCostMap(M.cost_map, M.x_range, M.y_range);
P = P.setCostMap(noise_map + blur_map, M.x_range, M.y_range);
alpha_path = P.linearAlphaPath(start_alphas, alphas, TRAJ_STEPS);
q_cost = P.trajQCost(alpha_path);
ep_cost = P.endPointCost(alpha_path, contact_points);
eval_q = @(q) P.QCost_ind(q);
eval_path = @(path)  sum(P.trajQCost(path)) + P.endPointCost(alpha_path, contact_points);
S = STOMP(Q_INPUTS, TRAJ_STEPS, TRAJ_DT, eval_q, eval_path, NOISE_COOLING, g.jacobian_func(), @P.xy_path);
stomp_path = S.optimizeTraj(STOMP_STOP_COND, alpha_path, TRAJ_NOISE, NOISEY_TRAJS);
% implement dynamics and torque cost function
% implement successfu and failed grasps and good cost function space
xy_path = P.xy_path(stomp_path);
xy_max = max(xy_path);
xy_min = min(xy_path);
for i = 1:length(stomp_path)
    cla
    v = max(q_cost):-1:min(q_cost);
    contour(P.x_range, P.y_range, P.cost_map', v)
    g = g.calc_poses(stomp_path(i,:));
    g.draw(ax);
    obj.draw(ax);
    axis equal
    axis([-Inf,xy_max(1),-Inf, xy_max(2)])
    pause(0.01);
end

for i = 1:length(q_cost)
    if q_cost(i) > 4
        m = 'bo';
    else
        m = 'r*';
    end
    hold on; plot(xy_path(2*i-1,1), xy_path(2*i-1,2), m); hold off;
    hold on; plot(xy_path(2*i,1), xy_path(2*i,2), m); hold off;
end
%plot original trajectory also
xy_path_original = P.xy_path(alpha_path);
hold on; plot(xy_path_original(:,1), xy_path_original(:,2), 'g.'); hold off;
% figure(); hold on;
% for i = 1:length(alpha_path)
%     plot(xy_path(i,1), xy_path(i,2), 'bo')
%     pause(0.1)
% end
% hold off;
    


