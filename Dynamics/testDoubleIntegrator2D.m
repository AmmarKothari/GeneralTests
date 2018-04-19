D = DoubleIntegrator2D();

dt = 0.1;
t_all = 0:dt:10; 
for t=t_all
    u = [sin(t), cos(t)] + 0.1*(rand(1,2)-1);
    D=D.stepDynamics(u,dt);
    D=D.saveAll();
    
end

plot(D.q_all(:,1), D.q_all(:,2), 'rx')

%% move forward through dynamics
particle_count = 100;
D = DoubleIntegrator2D();
dt = 1;
colors = ['rgykc'];
i = 0;
avg_u = [5,5];
for noise = 1:5
    p_states = [];
    i = i + 1;
    i = min(i, rem(i, length(colors)+1));
        for p = 1:particle_count
            u = avg_u + noise*(rand(1,2)-0.5);
            D_step = D.stepDynamics(u,dt);
            p_states = [p_states; D_step.q'];
        end
    plot(p_states(:,1), p_states(:,2), strcat(colors(i),'x'))
    hold on
end
plot(0,0,'bo')
D_step = D.stepDynamics(avg_u,dt);
plot(D_step.q(1), D_step.q(2), 'k^')
hold off

%% resample based on measurement