clear all
addpath('../GeoMechanics_6D')
figure(1)
ax1 = gca();
global_pose = pose_class([0,0,0,0,0,0]);
object_pose = pose_class([1,1,1, 0,0,pi]);
h1_global = pose_class([1,0,1, 0, pi/4, 0]);
h2_global = pose_class([0,1,0, -pi/4, 0, 0]);

global_pose.plotPose(ax1, global_pose.p, 'rx');
object_pose.plotPose(ax1, object_pose.p, 'bo');

h1_global.plotPose(ax1, h1_global.p, 'g*');
hold on
h2_global.plotPose(ax1, h2_global.p, 'k*');
h2_relative_h1 = move_to_B(h1_global, h2_global);

c = global_pose.p(1:3); % need to find a center - not guaranteed to be equal distance from some point
% force that point to be the "center" - interpolate radius as well
% r = distance from center to ponit
v_c_1 = h1_global.p(1:3) - global_pose.p(1:3);
v_c_2 = h2_global.p(1:3) - global_pose.p(1:3); % vector from center to h2
u_v_c_1 = v_c_1/norm(v_c_1);
u_v_c_2 = v_c_2/norm(v_c_2);
r1 = sqrt(sum(v_c_1.^2));
r2 = sqrt(sum(v_c_2.^2));
h2_on_circle = u_v_c_2 * r1;
% build the plane
plane_normal = cross(v_c_1, v_c_2);
% equation of circle
circ = @(t,r) c + r*cos(t)*u_v_c_1 + r*sin(t)*u_v_c_2;
hold on
scatter3(ax1, h2_on_circle(1), h2_on_circle(2), h2_on_circle(3), 'k^')
hold off
% for i = 0:0.1:.9
%     qi = quatinterp(h1_global.q, h2_global.q, i, 'slerp'); % pose orientation
%     % for position orientation
%     T_mvd = trvec2tform(h1_global.p(1:3)*(1-i) + i*h2_global.p(1:3)) * quat2tform(qi); % linear
%     % spherical
%     T_mvd = trvec2tform(circ(i*pi/2, (1-i)*r1+i*r2)) * quat2tform(qi); % spherical
%     
%     hi_pose = pose_class(T_mvd);
%     hi_pose.plotPose(ax1);
% %     pause(1)
% end

figure(2)
ax2 = gca();
h1_local = move_to_B(object_pose, h1_global);
h2_local = move_to_B(object_pose, h2_global);
object_local = pose_class([0,0,0,0,0,0]);
object_local.plotPose(ax2, object_local.p, 'bo');
h1_local.plotPose(ax2, h1_local.p, 'g*');
hold on
h2_local.plotPose(ax2, h2_local.p, 'k*');

c = object_local.p(1:3); % need to find a center - not guaranteed to be equal distance from some point
% force that point to be the "center" - interpolate radius as well
% r = distance from center to ponit
v_c_1 = h1_local.p(1:3) - object_local.p(1:3);
v_c_2 = h2_local.p(1:3) - object_local.p(1:3); % vector from center to h2
u_v_c_1 = v_c_1/norm(v_c_1);
u_v_c_2 = v_c_2/norm(v_c_2);
r1 = sqrt(sum(v_c_1.^2));
r2 = sqrt(sum(v_c_2.^2));
h2_on_circle = u_v_c_2 * r1;
% find axis through the line to the plane between the points and
% perpinduclar to those points  -- implement current version in openrave
% see what central axis finder outputs


% build the plane
plane_normal = cross(v_c_1, v_c_2);
% equation of circle
circ = @(t,r) c + r*cos(t)*u_v_c_1 + r*sin(t)*u_v_c_2;

for i = 0:0.1:0.9
    qi = quatinterp(h1_local.q, h2_local.q, i, 'slerp');
    T_mvd = trvec2tform(h1_local.p(1:3)*(1-i) + i*h2_local.p(1:3)) * quat2tform(qi);  % for position orientation
    % spherical
    T_mvd = trvec2tform(circ(i*pi/2, (1-i)*r1+i*r2)) * quat2tform(qi); % spherical
    hi_pose = pose_class(T_mvd);
    hi_pose.plotPose(ax2);
    % interpolated poses in world frame
    hi_world = pose_class(object_pose.group * hi_pose.group);
    figure(1); hold on;
    hi_world.plotPose(ax1);
    figure(2); hold on;
end
hold off
