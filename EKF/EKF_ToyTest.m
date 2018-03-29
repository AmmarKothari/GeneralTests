% mapping theta acceleration to x and y position
% nonlinear

dt = 0.1;
t_total = 5;
N = t_total/dt;
L = 1;

m = 1; % number of measurements
n = 4; % number of states
uNoise = 0.01;
obsNoise = 0.01;
% theta_dd = 2/10*ones(N,1);
theta_dd = 1/10 * sin(0:dt:(t_total-dt)) + 0.2;
theta_dd_noise = theta_dd + randn(size(theta_dd))*uNoise;

% state = x,y,theta, thetad
s0 = [1, 0, 0, 0];
P0 = diag(ones(4,1));
est = struct('s', s0, 'P', P0);
prior = est;
post = est;
state_all = zeros(N, n);
z_all = zeros(N,m);
% state to state+1 transition
f = @(s,u) [L*cos(s(3)), L*sin(s(3)), s(3)+s(4)*dt, s(4)+u*dt]';

% state to measurement transition
h = @(s)  s(3);

Jf = @(s) [0, 0, -sin(s(3)),     0;
           0, 0,  cos(s(3)),     0;
           0, 0,        1,   1/100;
           0, 0,        0,     1];
   
Jh = zeros(m,n);

Q = diag(0.0001*ones(4,1));
R = 0.0001;

% run loop
i = 1;
for t = 0:dt:(t_total-dt)
    u = theta_dd_noise(i);
    z = post.s(3) + dt*post.s(4) + dt^2/2*u + randn(1)*obsNoise;
    % predict
    prior.s = f(post.s, u);
    prior.P = Jf(prior.s) * prior.P * Jf(prior.s)' + Q;
    % compute K gain
    K = prior.P * Jh' * inv(Jh * prior.P * Jh' + R);
    % correct/estimate
    post.s = prior.s + K * (z - h(prior.s));
    % compute covariance
    post.P = (eye(4) - K * Jh) * prior.P;
    % update values
    state_all(i,:) = post.s;
    z_all(i) = z;
    i = i +1;
    prior = post;
end

% actual values
theta_d = cumsum(theta_dd * dt);
theta = cumsum(theta_d *dt);
theta_d_noise = cumsum(theta_dd_noise * dt);
theta_noise = cumsum(theta_d_noise *dt);

% plot acceleration: ideal vs. noise
plot(1:N, theta_dd, 1:N, theta_dd_noise)

% plot velocity: ideal vs. noise vs. estimate
% plot(1:N, theta_d, 'rx', 1:N, theta_d_noise, 1:N, state_all(:,4), 'gx')

% plot theta: actual vs. measured vs. estimated
% plot(1:N, theta_noise, 'gx', 1:N, z_all, 'rx', 1:N, state_all(:,3), 'bo')

% plot x: actual vs. measured vs. estimated
% plot(1:N, L*cos(theta_noise), 'gx', 1:N, L*cos(z_all), 'rx', 1:N, L*cos(state_all(:,3)), 'bo')

% plot x: actual vs. measured vs. estimated
% plot(1:N, L*sin(theta_noise), 'gx', 1:N, L*sin(z_all), 'rx', 1:N, L*sin(state_all(:,3)), 'bo')

% plot the x,y position: actual vs. measured vs. estimated
x = L*cos(theta); y = L*sin(theta);
x_noise = L*cos(theta_noise); y_noise = L*sin(theta_noise);
% plot(L*cos(theta_noise), L*sin(theta_noise), 'gx', L*cos(z_all), L*sin(z_all), 'rx', L*cos(state_all(:,3)),L*sin(state_all(:,3)), 'bo')
% axis equal

% plot error in x position
plot(1:N, L*cos(state_all(:,3)) - L*cos(theta_noise)')

miny = min(L*sin(z_all)); maxy = max(L*sin(z_all));
minx = min(L*cos(z_all)); maxx = max(L*cos(z_all));
for i=1:N
    plot(L*cos(theta_noise(1:i)), L*sin(theta_noise(1:i)), 'gx',...
        L*cos(z_all(1:i)), L*sin(z_all(1:i)), 'rx', ...
        L*cos(state_all((1:i),3)),L*sin(state_all((1:i),3)), 'bo')
    xlim([minx, maxx]); ylim([miny, maxy]);
    pause(0.01)
end


