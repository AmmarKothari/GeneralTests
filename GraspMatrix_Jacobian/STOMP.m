classdef STOMP
    properties
       A
       R
       R_inv
       M
       DOF
       steps
       noise
       noisey_trajs
       dt
    end
    methods
        function obj = STOMP(dof, steps, noise, dt)
            obj.DOF = dof;
            obj.steps = steps;
            obj.noise = noise;
            %precompute
            obj.A = obj.computeA(steps, dt);
            obj.R = obj.A' * obj.A;
            obj.R_inv = inv(obj.R);
            obj.M = obj.computeM(obj.R_inv, steps);
            obj.dt = dt;
        end
        
        
        function obj = noiseyTrajs(obj, alpha_path, noise, n_trajs)
            obj.noisey_trajs = zeros(size(alpha_path, 1), size(alpha_path, 2), n_trajs);
            for i = 1:n_trajs
                obj.noisey_trajs(:, :, i) = obj.noisyTraj(alpha_path, obj.R_inv, noise);
            end
%             obj.plotNoiseyTrajs(alpha_path, obj.noisey_trajs);
        end
        
    end
    
    methods(Static)
        function A = computeA(steps, dt)
            % theta is how many controllable dofs
            % steps is number of steps in trajectory
            N = steps;
            % inbuilt function to make diagonal matrix
            A = full(gallery('tridiag',N,1,-2,1));
            % add row with one at top and bottom
            A = [1, zeros(1,size(A,2)-1); A; zeros(1,size(A,2)-1), 1];
            A = A ./ (dt^2);
        end
        
        function M = computeM(R_inv, N)
            M = R_inv./max(R_inv)/N;
        end
        
        function noisy_traj = noisyTraj(alpha_path, R_inv, noise)
            % generates a single noisy trajectory
            % should the noise be scaled to the joint limits?
            noisy_traj = alpha_path + mvnrnd(zeros(1,size(alpha_path,1)), R_inv)' * noise;
        end
        
        function [] = plotNoiseyTrajs(alpha_path, noisey_trajs)
            figure(2);
            plot(alpha_path(:,1), 'ro');
            hold on;
            for i = 1:size(noisey_trajs, 3)
                plot(noisey_trajs(:,1, i), 'xb');
            end
            hold off
        end
        
        function [] = plotCovariance(R_inv)
            figure();
            for i = 1:size(R_inv,2)
                plot(R_inv(:,i), 'x')
                hold on;
            end
            hold off
        end
                
        
    end
end