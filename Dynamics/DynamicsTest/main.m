% free floating link, testing out different combinations of forces and
% torques
group = @(pose) [cos(pose(3)), -sin(pose(3)), pose(1); sin(pose(3)), cos(pose(3)), pose(2); 0, 0, 1];
pose = @(group) [group(1,3), group(2,3), atan2(group(2,1), group(1,1))];
I_rod = @(m, l) 1/12*m*l^2; % inertia of rod rotating about base

l1 = 1;
r1 = l1/2;
m1 = 1;
% I1 = I_rod(m1) + l1/2*m1^2; %inertia of a rod rotating about its base
I1 = I_rod(m1,l1); %inertia of a rod rotating about its center

t_total = 10;
n_total = 1000;
dt = t_total/n_total;

p0 = [0,0,0];
P0 = [];

p1 = [l1,0,0];
P1 = [];

f1 = [0.1, 0];
f2_neg = [0, 0];
n1 = [0];
n2_neg = [0.5];

p1_cm = 0; a1_cm = 0; v1_cm = 0;
P1_CM = []; A1_CM = []; V1_CM = [];
P1 = []; P2 = [];
t1_cm = 0; alpha1_cm = 0; w1_cm = pi./2;
T1_CM = []; ALPHA1_CM = []; W1_CM = [];

e = 0; e_prev = 0; e_sum = 0;
E = []; E_DIF = []; E_SUM = [];

cla(figure(1));
cla(figure(2));
for t=1:dt:t_total

    F1 = f1 + f2_neg;
    n_f1 = cross([-r1, 0, 0], [f1,0]);
    n_f2_neg = cross([r1, 0, 0], [f2_neg,0]);
    % gyroscopic torque only plays a part in 3d because axis of rotation is
    % always aligned with angular momentum 
    N1 = n1 - n2_neg + n_f1(1) - n_f2_neg(1);
    a1_cm = F1/m1;
    alpha1_cm  = inv(I1) * N1;
    p1_cm = p1_cm + v1_cm * dt + 1/2*a1_cm*dt;
    t1_cm = t1_cm + w1_cm * dt + 1/2*alpha1_cm*dt;
    v1_cm = v1_cm + a1_cm * dt;
    w1_cm = w1_cm + alpha1_cm * dt;
    R_cm_1 = group([-r1, 0, 0]);
    R_cm_2 = group([r1, 0, 0]);
    p1 = pose(group([p1_cm, t1_cm]) * R_cm_1);
    p2 = pose(group([p1_cm, t1_cm]) * R_cm_2);
    ALPHA1_CM = [ALPHA1_CM; alpha1_cm];
    W1_CM = [W1_CM; w1_cm];
    A1_CM = [A1_CM; a1_cm];
    P1_CM = [P1_CM; p1_cm];
    V1_CM = [V1_CM; v1_cm];
    P1 = [P1; p1];
    P2 = [P2; p2];
    if rem(t,.1) < 1e-4
        figure(1); hold on; plot([p1(1,1), p2(1,1)], [p1(1,2), p2(1,2)], 'ro-'); plot(p2(1,1), p2(1,2), 'bo')
    end
%     e_prev = e;
%     e = w1_cm;
%     e_sum = e_sum + e;
%     e_dif = e - e_prev;
%     E = [E; e];
%     E_SUM = [E_SUM; e_sum];
%     E_DIF = [E_DIF; e_dif];
%     P = 0.1; I = 1e-3; D = 0;
%     n2_neg =  P * e + I*e_sum + D*e_dif* 0.1;
end
figure(2)
plot(1:length(P1_CM), P1_CM(:,1), 'rx', 1:length(P1_CM), P1_CM(:,2), 'bx');
figure(3); plot(W1_CM, 'rx'); title('Omega');
figure(4); plot(1:length(E), E, 'r', 1:length(E), E_SUM, 'b', 1:length(E), E_DIF, 'g')