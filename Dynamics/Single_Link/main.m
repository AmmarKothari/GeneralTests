% trying out dynamics for a single link system

l1 = 1;
m = 0.5;
p_0 = [0,0];
j1 = 0; %joint angle
J1 = []; %
w1 = 0; % joint velocity
W1 = [];
alpha1 = 0; % angular acceleration
torque1 = 0.01; % applied torque
I_rod = 1/12*m*l1^2; % inertia of rod rotating about base
I1 = I_rod + l1/2*m^2; %inertia of a rod rotating about its base
t_end = 40; % time
dt = 0.01; % timestep
p1_0 = [l1,0,0]; % pose at end of link
p1 = [];
v1 = []; % velocity at the end point;
v1_dif = []; % velocity at the end point from finite difference
a1 = []; % acceleration at the end point;
F1 = []; % force at the end point

mu = 0.1; %joint friction
% Fend_f = @(theta,x) 0.1 * [cos(theta)*(x) sin(theta)*x]; % constant force on the end
Fend_f = @(theta,x) -1e-3*[sin(theta), cos(theta)] ; % constant force on the end perpendicular to rod - counteract torque 0.01

% % % DYNAMICS % % %
% goal: generate a force at the end effector
u1 = []; % control input needed to achieve Fend_f
for t = 0:dt:t_end
    % forward
%     alpha1 = inv(I1) * torque1;
    w1 = w1 + (alpha1 - sign(w1)*mu*w1) * dt;
    W1 = [W1;w1];
    j1 = j1 + w1 * dt + 1/2 * alpha1 * dt^2;
    R = [cos(j1), -sin(j1), 0; sin(j1), cos(j1), 0; 0, 0, 1];
    p1 = [p1; (R * p1_0')'];
    v1 = [v1; cross([0,0,w1], [p1(end,1), p1(end,2), 0])];
    a1 = [a1; alpha1*cos(j1)*l1, alpha1*sin(j1)*l1];
    % backward
    
    Fend = Fend_f(j1, t); % some force applied at the end point
    torque1_effective = inv(m) * norm(Fend); % torque induced by force
    alpha1_effective = inv(I1) * torque1_effective; % effective alpha at the link
    u1 = [u1; alpha1_effective];
    alpha1 = alpha1_effective;
end
% hold on;
figure(1); plot(p1(:,1), p1(:,2), 'ro'); title('Position')
ppt = 25;
% quiver(p1(1:ppt:end,1), p1(1:ppt:end,2), v1(1:ppt:end,1), v1(1:ppt:end,2))
% hold off;
figure(2); plot(1:length(v1), v1(:,1), 'ro', 1:length(v1), v1(:,2), 'bo'); title('Velocity')
figure(3); plot(1:length(a1), a1(:,1), 'ro', 1:length(a1), a1(:,2), 'bo'); title('Acceleration')
axis square
figure(4); plot(1:length(u1), u1(:), 'bx'); title('U1');




% reverse
