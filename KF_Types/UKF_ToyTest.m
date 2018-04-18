% mapping theta acceleration to x and y position
% nonlinear
% more parameters that can be tuned in exchange for better prediction

dt = 0.1;
t_total = 10;
N = t_total/dt;
L = 1;

m = 1; % number of measurements
n = 4; % number of states
uNoise = 1e-2;
obsNoise = 1e-2;
% theta_dd = 2/10*ones(N,1);
theta_dd = 1/10 * sin(0:dt:(t_total-dt));% + 0.2;
theta_dd_noise = theta_dd + randn(size(theta_dd))*uNoise;

% UKF Constants
alpha = 1e2; % increasing alpha makes it follow measurements closer; vary as a ratio of state (n)
kappa = 1e-3; % same type of trend as alpha
lambda = alpha^2*(n+kappa)-n;
gamma = sqrt(n+lambda);
Beta = 2; % assuming gaussian distribution
weights_m = [lambda/(n+lambda), ones(1,2*n).*1/2/(n+lambda)];
weights_c = [lambda/(n+lambda) + (1-alpha^2+Beta), ones(1,2*n).*1/2/(n+lambda)];

% actual values
theta_d = cumsum(theta_dd * dt);
theta = cumsum(theta_d * dt);
theta_d_noise = cumsum(theta_dd_noise * dt);
theta_noise = cumsum(theta_d_noise * dt);

% state = x,y,theta, thetad
s0 = [1, 0, 0, 0]';
P0 = diag(ones(4,1));
est = struct('s', s0, 'P', P0);
prior = est; meas = est; post = est;

% state to state+1 transition
f = @(s,u) [L*cos(s(3)), L*sin(s(3)), s(3)+s(4)*dt, s(4)+u*dt]';

% state to measurement transition
h = @(s)  s(3);

R = diag(1e-2*ones(4,1));
Q = 1e1;

% run loop
state_all = zeros(N, n);
z_all = zeros(N,m);
i_t = 1;
t_range = 0:dt:(t_total-dt);
for t = t_range
    u = theta_dd_noise(i_t);
    z = theta_noise(i_t) + dt*theta_d_noise(i_t) + dt^2/2*u + randn(1)*obsNoise;
    % % State Update
    % generate sigma points
    sigma_pts_state = [post.s, post.s + sqrt((n+gamma)*diag(post.P)).*eye(n), post.s - sqrt((n+gamma)*diag(post.P)).*eye(n)];
    % pass through function
    f_sigma_pts_state = [];
    for i = 1:(2*n+1)
        f_sigma_pts_state = [f_sigma_pts_state, f(sigma_pts_state(:,i), u)];
    end
    % estimate mu and covariance
    prior.s = (weights_m * f_sigma_pts_state')';
    prior.P = prior.P*0;
    for i = 1:(2*n+1)
        prior.P = prior.P + weights_c(i)*(f_sigma_pts_state(:,i) - prior.s)*(f_sigma_pts_state(:,i) - prior.s)';
    end
    prior.P = prior.P + R;
    
    % % Measurement Update
    % generate sigma points
    sigma_pts_meas = [prior.s, prior.s + sqrt((n+gamma)*diag(prior.P)).*eye(n), prior.s - sqrt((n+gamma)*diag(prior.P)).*eye(n)];
    % pass through function
    h_sigma_pts_state = [];
    for i = 1:(2*n+1)
        h_sigma_pts_state = [h_sigma_pts_state, h(sigma_pts_meas(:,i))];
    end
    % estimate mu and covariance
    meas.s = weights_m * h_sigma_pts_state';
    meas.P = zeros(m,m);
    for i = 1:(2*n+1)
        meas.P = meas.P + weights_c(i)*(h_sigma_pts_state(:,i) - meas.s')*(h_sigma_pts_state(:,i) - meas.s')';
    end
    meas.P = meas.P + Q;
    % compute cross covariance
    cross_covariance = meas.P*0;
    for i = 1:(2*n+1)
        cross_covariance = cross_covariance + weights_c(i)*(f_sigma_pts_state(:,i) - prior.s)*(h_sigma_pts_state(:,i) - meas.s')';
    end
    % compute K gain
    K = cross_covariance * inv(meas.P);
    % correct/estimate
    post.s = prior.s + K * (z - meas.s);
    % compute covariance
    post.P = prior.P - K*meas.P*K';
    % update values
    state_all(i_t,:) = post.s;
    z_all(i_t) = z;
    i_t = i_t +1;
    prior = post;
end

% plot acceleration: ideal vs. noise
% plot(1:N, theta_dd, 1:N, theta_dd_noise)

% plot velocity: ideal vs. noise vs. estimate
% plot(1:N, theta_d, 'rx', 1:N, theta_d_noise, 1:N, state_all(:,4), 'gx')

% plot theta: actual vs. measured vs. estimated
% plot(1:N, theta_noise, 'gx', 1:N, z_all, 'rx', 1:N, state_all(:,3), 'bo')

% plot x: actual vs. measured vs. estimated
% plot(1:N, L*cos(theta_noise), 'gx', 1:N, L*cos(z_all), 'rx', 1:N, L*cos(state_all(:,3)), 'bo')

% plot x: actual vs. measured vs. estimated
plot(1:N, L*sin(theta_noise), 'g*', 1:N, L*sin(z_all), 'rx', 1:N, state_all(:,2), 'bo')
legend('XY Actual', 'XY from measured Theta', 'XY Estimate')

% plot the x,y position: actual vs. measured vs. estimated
x = L*cos(theta); y = L*sin(theta);
x_noise = L*cos(theta_noise); y_noise = L*sin(theta_noise);
% plot(L*cos(theta_noise), L*sin(theta_noise), 'gx', L*cos(z_all), L*sin(z_all), 'rx', state_all(:,1),state_all(:,2), 'bo')
% axis equal

% plot error in x position
% figure(1)
% subplot(2,1,1)
% plot(t_range, L*cos(state_all(:,3)) - L*cos(theta_noise)', 'bx-')
% subplot(2,1,2)
% plot(t_range, theta_noise, 'ro-')
% 
% figure(2)
% miny = min(L*sin(z_all)); maxy = max(L*sin(z_all));
% minx = min(L*cos(z_all)); maxx = max(L*cos(z_all));
% for i=1:N
%     plot(L*cos(theta_noise(1:i)), L*sin(theta_noise(1:i)), 'gx',...
%         L*cos(z_all(1:i)), L*sin(z_all(1:i)), 'rx', ...
%         state_all(1:i,1),state_all(1:i,3), 'bo')
%     xlim([minx, maxx]); ylim([miny, maxy]);
%     pause(0.01)
% end


