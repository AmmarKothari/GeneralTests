N = 1000;
u = ones(N,2).*[0.5, 0.3];
D = DiffDrive(1, 1e-2, [0.5, 0.5], [0.1, 0.1, 0.1]);

for i = 1:length(u)
    D = D.step_dynamics(u(i,:));
    D = D.recordData();
    D = D.getOdometry();
    
    
end

D.plotRecordedState();
hold on
D.plotObservedState();
hold off