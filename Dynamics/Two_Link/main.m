clear all
% trying out dynamics for a two link system
group = @(pose) [cos(pose(3)), -sin(pose(3)), pose(1); sin(pose(3)), cos(pose(3)), pose(2); 0, 0, 1];
pose = @(group) [group(1,3), group(2,3), atan2(group(2,1), group(1,1))];
I_rod = @(m, l) 1/12*m*l^2; % inertia of rod rotating about base

l1 = 1; r1 = l1/2; m1 = 0.5; R_cm1_p = group([-r1, 0, 0]); R_cm1_d = group([r1, 0, 0]);
l2 = 0.5; r2 = l2/2; m2 = 0.25; R_cm1_p = group([-r2, 0, 0]); R_cm1_d = group([r2, 0, 0]);

p1_cm = [0,0]; P1_CM = []; a1_cm = []; A1_CM = []; v1_cm = [0,0]; V1_CM = [];
p2_cm = []; P2_CM = []; a2_cm = 0; A2_CM = []; v2_cm = 0; V2_CM = [];

j1 = 0; J1 = []; w1 = 0; W1 = []; alpha1 = 0; ALPHA1 = [];
j2 = 0; J2 = []; w2 = 0; W2 = []; alpha2 = 0; ALPHA2 = [];


t1_cm = 0; alpha1_cm = 0; w1_cm = 0;
T1_CM = []; ALPHA1_CM = []; W1_CM = [];
t2_cm = 0; alpha2_cm = 0; w2_cm = 0;
T2_CM = []; ALPHA2_CM = []; W2_CM = [];

I1 = I_rod(m1,l1); %inertia of a rod rotating about its center
I2 = I_rod(m2,l2); 

P1 = []; % position of the joint
P2 = [];
V1 = []; % velocity of the joint
V2 = [];
A1 = []; % acceleration of the joint
A2 = [];
F1 = []; % force of the joint
F2 = [];

mu = 0.0; %joint friction
% Fend_f = @(theta,x) 0.1 * [cos(theta)*(x) sin(theta)*x]; % constant force on the end
% Fend_f = @(theta,x) -1e-3*[sin(theta), cos(theta)] ; % constant force on the end perpendicular to rod - counteract torque 0.01

torque1 = 0.02; % applied torque
torque2 = -0.00;
f1 = [0, 0]; f2 = [0, 0]; %no forces acting on joints
f1_neg = -f1; f2_neg = -f2;

% % % DYNAMICS % % %
% goal: generate a force at the end effector
u1 = []; % control input needed to achieve Fend_f


t_end = 40; % time
n_steps = 1000;
dt = t_end/n_steps; % timestep
cla(figure(1));
for t = 0:dt:t_end
    % FIRST JOINT    
    % forward
    F1 = f1 + f2_neg;
    n_f1 = cross([-r1, 0, 0], [f1, 0]);
    n_f2_neg = cross([r1, 0, 0], [f2_neg,0]);
    N1 = torque1 - torque2 + n_f1 + n_f2_neg;
    a1_cm = F1/m1;
    alpha1_cm = inv(I1) * N1;
    
    % CM changes
    p1_cm = p1_cm + v1_cm * dt + 1/2*a1_cm*dt;
    t1_cm = t1_cm + w1_cm * dt + 1/2*alpha1_cm*dt;
    v1_cm = v1_cm + a1_cm * dt;
    w1_cm = w1_cm + alpha1_cm * dt;
    p1 = pose(group([p1_cm, t1_cm]) * R_cm1_p);
    p2 = pose(group([p1_cm, t1_cm]) * R_cm1_d); 
    
    % joint changes
    j1 = j1 + w1 * dt + 1/2 * alpha1 * dt^2;
    w1 = w1 + alpha1 * dt;
    R1 = [cos(j1), -sin(j1), 0; sin(j1), cos(j1), 0; 0, 0, 1];
    v2 = cross([0,0,w1], [p1_cm(1), p1_cm(2), 0]);
    a2 = [alpha1*cos(j1)*l1, alpha1*sin(j1)*l1];
    
    W1_CM = [W1_CM; w1_cm];
    A1_CM = [A1_CM; a1_cm];
    P1_CM = [P1_CM; p1_cm];
    V1_CM = [V1_CM; v1_cm];
    P1 = [P1; p1];
    P2 = [P2; p2];
    
    if rem(t,.1) < 1e-4
        figure(1); hold on; plot([p1(1,1), p2(1,1)], [p1(1,2), p2(1,2)], 'ro-'); plot(p2(1,1), p2(1,2), 'bo')
    end
    
%     alpha2 = inv(I2) * torque2 - sign(w2)*mu*w2;
%     j2 = j2 + w2 * dt + 1/2 * alpha2 * dt^2;
%     w2 = w2 + alpha2 * dt;
%     R2 = group([cos(j2), -sin(j2), 0; sin(j2), cos(j2), 0; 0, 0, 1] * p2_0');
%     p2_cm = pose(group(p1_cm) * R2);
%     
%     ALPHA2 = [ALPHA2; alpha2];
%     W2 = [W2;w2];
%     J2 = [J2;j2];
%     P2_CM = [P2_CM; p2_cm];
%     V2 = [V2; v2];
%     A2 = [A2; a2];
    
    % backward
    
%     Fend = Fend_f(j1, t); % some force applied at the end point
%     torque1_effective = inv(m) * norm(Fend); % torque induced by force
%     alpha1_effective = inv(I1) * torque1_effective; % effective alpha at the link
%     u1 = [u1; alpha1_effective];
%     alpha1 = alpha1_effective;
end




% hold on;
% figure(1); plot(P1_CM(:,1), P1_CM(:,2), 'ro', P2_CM(:,1), P2_CM(:,2), 'bo'); title('Position')
% ppt = 25;
% % quiver(p1(1:ppt:end,1), p1(1:ppt:end,2), v1(1:ppt:end,1), v1(1:ppt:end,2))
% % hold off;
% figure(2); plot(1:length(W1), W1(:,1), 'ro', 1:length(W2), W2(:,1), 'bo'); title('Velocity')
% figure(3); plot(1:length(ALPHA1), ALPHA1(:,1), 'ro', 1:length(ALPHA2), ALPHA2(:,1), 'bo'); title('Acceleration')
% axis square
% figure(4); plot(1:length(J1), J1, 'rx', 1:length(J2), J2, 'bx'); title('Joint Angles')
% figure(4); plot(1:length(u1), u1(:), 'bx'); title('U1');




% reverse
