% which should be calculated first, velocity or position?


% pendulum swing
t_total = 1000;
N = 100000;
dt = t_total/N;
theta = pi/2; w = 0; alpha = 0;
THETA=[]; W=[]; ALPHA=[];
g = -9.8;
l = 1; r=l/2;
k = 0.0; %Couloumb friction in joint
cla(figure(1));

% updating theta and then w <-- THIS ONE!
for t = 1:dt:t_total
    alpha = 1/r*g*sin(theta) - sign(w)*k;
    theta = theta + w*dt + 1/2*dt^2*alpha;
    w = w + alpha*dt;
    THETA = [THETA; theta];
    W = [W; w];
    ALPHA = [ALPHA; alpha];
end

figure(1)
subplot(3,1,1); plot(THETA, 'rx'), title('Theta');
subplot(3,1,2); plot(W, 'rx'), title('Omega');
subplot(3,1,3); plot(ALPHA, 'rx'), title('Alpha');
suptitle('Theta then W');

theta = pi/2; w = 0; alpha = 0;
THETA=[]; W=[]; ALPHA=[];
% updating w and then theta
for t = 1:dt:t_total
    alpha = 1/r*g*sin(theta) - sign(w)*k;
    w = w + alpha*dt;
    theta = theta + w*dt;
    THETA = [THETA; theta];
    W = [W; w];
    ALPHA = [ALPHA; alpha];
end

figure(2)
subplot(3,1,1); plot(THETA, 'rx'), title('Theta');
subplot(3,1,2); plot(W, 'rx'), title('Omega');
subplot(3,1,3); plot(ALPHA, 'rx'), title('Alpha');
suptitle('W then Theta');




