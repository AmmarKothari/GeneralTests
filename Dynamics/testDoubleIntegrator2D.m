D = DoubleIntegrator2D();

dt = 0.1;
t_all = 0:dt:10; 
for t=t_all
    u = [sin(t), cos(t)] + 0.1*(rand(1,2)-1);
    D=D.stepDynamics(u,dt);
    D=D.saveAll();
    
end

plot(D.q_all(:,1), D.q_all(:,2), 'rx')

