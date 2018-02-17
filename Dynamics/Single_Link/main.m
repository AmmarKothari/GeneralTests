% trying out dynamics for a single link system

l1 = 1;
m = 0.5;
p_0 = [0,0];
j1 = 0; %joint angle
w1 = 0; % joint velocity
alpha1 = 0; % angular acceleration
torque1 = 0.01; % applied torque
I_rod = 1/12*m*l1^2; % inertia of rod rotating about base
I1 = I_rod + l1/2*m^2; %inertia of a rod rotating about its base
t_end = 20; % time
dt = 0.01; % timestep
p1_0 = [l1,0,0]; % pose at end of link
p1 = [];
v1 = []; % velocity at the end point;
v1_dif = []; % velocity at the end point from finite difference
a1 = []; % acceleration at the end point;
F1 = []; % force at the end point

% Fend_f = @(theta,x) 0.1 * [cos(theta)*(x) sin(theta)*x]; % constant force on the end
Fend_f = @(theta,x) -0.01*[sin(theta), cos(theta)] ; % constant force on the end perpendicular to rod - counteract torque 0.01

% % % DYNAMICS % % %
% goal: generate a force at the end effector
F_des = 1;
for t = 0:dt:t_end
    % forward
    alpha1 = inv(I1) * torque1;
    w1 = w1 + alpha1 * dt;
    j1 = j1 + w1 * dt + 1/2 * alpha1 * dt^2;
    R = [cos(j1), -sin(j1), 0; sin(j1), cos(j1), 0; 0, 0, 1];
    p1 = [p1; (R * p1_0')'];
    v1 = [v1; cross([0,0,w1], [p1(end,1), p1(end,2), 0])];
    a1 = [a1; alpha1*cos(j1)*l1, alpha1*sin(j1)*l1];
    % backward
    F1 = [F1; m*a1(end,:) + F_des];
    T1 = [0, 0, F_des];
    
    Fend = Fend_f(j1, t); % some force applied at the end point
    torque1_effective = inv(m) * norm(Fend); % torque induced by force
    alpha1_effective = alpha1 + inv(I1) * torque1_effective; % effective alpha at the link
    
end
% hold on;
figure(1); plot(p1(:,1), p1(:,2), 'ro')
ppt = 25;
% quiver(p1(1:ppt:end,1), p1(1:ppt:end,2), v1(1:ppt:end,1), v1(1:ppt:end,2))
% hold off;
figure(2); plot(1:length(v1), v1(:,1), 'ro', 1:length(v1), v1(:,2), 'bo')
figure(3); plot(1:length(a1), a1(:,1), 'ro', 1:length(a1), a1(:,2), 'bo');
axis square




% reverse
