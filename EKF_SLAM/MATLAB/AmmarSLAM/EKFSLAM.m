function EKFSLAM(config_fn)
% main file
% call this with config file to run SLAM

% config_fn should not have .m at the end
eval(config_fn)

vehicle = DiffDrive(dt_sim, );
map = Map1();
sensor = PlanarLidarSensor();
mapper = Mapper();

% run through simulation loop
for t = 0:0.01:5
    
    
    
end