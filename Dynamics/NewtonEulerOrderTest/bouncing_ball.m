% which should be calculated first, velocity or position?


% pendulum swing
t_total = 10;
N = 1000;
dt = t_total/N;
h = 10; v_h = 0;
H = []; V_H = [];
g = -9.8;
k = 0.0; %energy dissipation when it hits the ground
cla(figure(1));
cla(figure(2));

% updating theta and then w <-- THIS ONE!
for t = 1:dt:t_total
    % bounce condition
    if h < 0
        v_h = -v_h;
    end
    v_h = v_h + g*dt;
    h = h + v_h*dt;
    H = [H;h];
    V_H = [V_H;v_h];
end
fprintf("Max H: %f\n", max(H));

figure(1)
subplot(2,1,1); plot(H, 'rx'), title('Height');
subplot(2,1,2); plot(V_H, 'rx'), title('Velocity');
suptitle('V then H');

h = 10; v_h = 0;
H = []; V_H = [];
% updating theta and then w
for t = 1:dt:t_total
    % bounce condition
    if h < 0
        v_h = -v_h;
    end
    h = h + v_h*dt;
    v_h = v_h + g*dt;
    H = [H;h];
    V_H = [V_H;v_h];
end
fprintf("Max H: %f\n", max(H));

figure(2)
subplot(2,1,1); plot(H, 'rx'), title('Height');
subplot(2,1,2); plot(V_H, 'rx'), title('Velocity');
suptitle('V then H');
