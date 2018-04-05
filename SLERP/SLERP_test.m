
addpath('../GeoMechanics_6D')
figure(1)
ax1 = gca();
h1_global = pose_class([1,0,0, 0, 0, 0]);
h2_global = pose_class([0,1,0, 0, 0, pi/2]);
global_pose = pose_class([0,0,0,0,0,0]);
object_pose = pose_class([1,1,0, 0,0,pi]);

global_pose.plotPose(ax1, global_pose.p, 'rx');
object_pose.plotPose(ax1, object_pose.p, 'bo');

h1_global.plotPose(ax1, h1_global.p, 'g*');
hold on
h2_global.plotPose(ax1, h2_global.p, 'k*');

for i = 0:0.1:.5
    qi = quatinterp(quatnormalize(h1_global.q), quatnormalize(h2_global.q), i, 'slerp');
    pt_mvd = quat2tform(qi) * [h1_global.p(1:3),1]';
    T_mvd = [quat2rotm(qi), pt_mvd(1:3); 0,0,0,1];
    hi_pose = pose_class(T_mvd);
    hi_pose.plotPose(ax1);
end

figure(2)
ax2 = gca();
h1_local = move_from_A_to_B(global_pose, object_pose, h1_global);
h2_local = move_from_A_to_B(global_pose, object_pose, h2_global);
object_local = pose_class([0,0,0,0,0,0]);
object_local.plotPose(ax2, object_local.p, 'bo');
h1_local.plotPose(ax2, h1_local.p, 'g*');
hold on
h2_local.plotPose(ax2, h2_local.p, 'k*');

for i = 0:0.1:.5
    qi = quatinterp(quatnormalize(h1_local.q), quatnormalize(h2_local.q), i, 'slerp');
    pt_mvd = quat2tform(qi) * [-h1_local.p(1:3),1]';
    T_mvd = [quat2rotm(qi), pt_mvd(1:3); 0,0,0,1];
    hi_pose = pose_class(T_mvd);
    hi_pose.plotPose(ax2);
end
hold off
