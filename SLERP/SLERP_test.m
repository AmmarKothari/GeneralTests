
addpath('../GeoMechanics_6D')
h1_pose = pose_class([1,0,0, 0, 0, 0]);
h2_pose = pose_class([0,1,0, 0, 0, pi/2]);

scatter3(h1_pose.p(1), h1_pose.p(2), h1_pose.p(3), 'rx')
hold on
scatter3(h2_pose.p(1), h2_pose.p(2), h2_pose.p(3), 'bx')

qi = quatinterp(quatnormalize(h1_pose.q), quatnormalize(h2_pose.q), 0.5, 'slerp');
hi_pose = pose_class(quat2tform(qi));
hold off