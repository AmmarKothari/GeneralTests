clear all
% trying out dynamics for a two link system
group = @(pose) [cos(pose(3)), -sin(pose(3)), pose(1); sin(pose(3)), cos(pose(3)), pose(2); 0, 0, 1];
pose = @(group) [group(1,3), group(2,3), atan2(group(2,1), group(1,1))];
I_rod_CM = @(m, l) 1/12*m*l^2; % inertia of rod rotating about base
I_rod_end = @(m,l) I_rod_CM(m,l) + m*(l/2)^2;

l1 = 1; m1 = 0.5;
l2 = 0.5; m2 = 0.25;

link1 = link(l1, m1);
link2 = link(l2,m2);



t_end = 40; % time
n_steps = 1000;
dt = t_end/n_steps; % timestep
cla(figure(1));
for t = 0:dt:t_end
    link1.torque = 1*sin(t);
    
    %Forward
    link1.j = link1.j + dt*link1.w + 1/2*dt^2*link1.alpha;
    link1.w = link1.w + dt*link1.alpha;
    out = inv(link1.group([0,0,link1.j]))*[link1.alpha*link1.r, -link1.w^2*link1.r, 0]';
    link1.a_cm = out(1:2)';
    link1.p_cm = link1.p_cm + dt*link1.v_cm + 1/2*dt^2*link1.a_cm;
    link1.v_cm = link1.v_cm + dt*link1.a_cm;
    
    link1.a_d = link1.alpha*link1.l*[cos(link1.j),sin(link1.j)];
    link1.p_d = link1.p_d + dt*link1.v_d + 1/2*dt^2*link1.a_d;
    link1.v_d = link1.v_d + dt*link1.a_d;
    
    link2.a_p = link1.a_d;
    link2.p_p = link1.p_d;
    link2.v_p = link2.v_d;
    
    link2.a_cm = link2.a_p + (link2.alpha*link2.r)*[cos(link2.j+link1.j), sin(link2.j+link1.j)];
    
       
    
    
    % Backward
    
    % solve for alpha2
    link2.alpha = inv(link2.I_end) * link2.torque;
    
    % solve for joint forces
    link2.O_n = -link2.m * link2.w^2 * link2.r;
    link2.O_t = link2.m*link2.alpha*link2.r;
    
    % convert to frame of previous link
    out = inv(link2.group([0,0,link2.j+link1.j])) *  [link2.O_n, link2.O_t, 0]';
    link2.O_x = out(1);
    link2.O_y = out(2);
    link1.O_d_x = -link2.O_x;
    link1.O_d_y = -link2.O_y;
    out = link2.group([0,0,link2.j+link1.j]) *  [link1.O_d_x, link1.O_d_y, 0]';
    link1.O_d_n = out(1);
    link1.O_d_t = out(2);
    
    % solve for alpha1
    link1.alpha = (link1.torque + link1.O_d_t*link1.r) * inv(link1.I_end);
    
    link1 = link1.store_values();
    link2 = link2.store_values();
    link1.plot_CM(1);
    
    
end
