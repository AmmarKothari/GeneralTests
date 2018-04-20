addpath('../Dynamics')
cla;
% % move forward through dynamics
particle_count = 10;
D = DoubleIntegrator2D();
dt = 1;
colors = ['rgykc'];
i = 0;
avg_u = [0.1,0.1];
weight = 1/particle_count*ones(particle_count,1);
weight_update = 01;
p_states = zeros(particle_count,6);
action_noise = 0.05;
i = i + 1;
i = min(i, rem(i, length(colors)+1));
for t=1:100
    for p = 1:particle_count
        u = avg_u + action_noise*(rand(1,2)-0.5);
        D_step = D.setState(p_states(p,1:2)', p_states(p,3:4)', p_states(p,5:6)');
        D_step = D_step.stepDynamics(u,dt);
        p_states(p,:) = [D_step.q', D_step.qd', D_step.qdd'];
    end
    plot(p_states(:,1), p_states(:,2), strcat(colors(i),'x'))
    hold on
    plot(0,0,'bo')
    D = D.stepDynamics(avg_u,dt);
    plot(D_step.q(1), D_step.q(2), 'k^')

    % % resample based on measurement

    meas = D.q;
    meas_noise = rand(2,1);
    dist = @(x,y) norm(x-y);
    new_weight = zeros(particle_count,1);
    for p=1:particle_count
        new_weight(p) = dist(meas+meas_noise, p_states(p,1:2));
    end
    new_weight = new_weight/sum(new_weight);
    weight = (weight + weight_update*new_weight);
    weight = weight/sum(weight);
    keep_weights = weight;
    keep_states = zeros(particle_count,6);
    for p = 1:particle_count
        val = rand(1);
        s = find((cumsum(weight) - val)>0,1);
        keep_states(p,:) = p_states(s,:);
        keep_weights(p) = weight(s);
    end

    plot(keep_states(:,1), keep_states(:,2), 'bo')
    
    p_states = keep_states;
    weight = keep_weights;
    pause(0.1)
end