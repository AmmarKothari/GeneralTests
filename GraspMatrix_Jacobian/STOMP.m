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
       eval_state
       eval_path
       %
       debugSTOMP1
    end
    methods
        function obj = STOMP(dof, steps, noise, dt, eval_state, eval_path)
            obj.DOF = dof;
            obj.steps = steps;
            obj.noise = noise;
            obj.eval_state = eval_state; % function to evaluate cost of a state
            obj.eval_path = eval_path; % function to evaluate cost of path
            %precompute
            obj.A = obj.computeA(steps);
            obj.R = obj.A' * obj.A;
            obj.R_inv = inv(obj.R);
            obj.M = obj.computeM(obj.R_inv, steps);
            obj.dt = dt;
            
            obj.debugSTOMP1 = false;  %plot noisey trajectories
        end
        
        
        function [noisey_trajs, noises] = noiseyTrajs(obj, alpha_path, noise, n_trajs)
            noisey_trajs = zeros(size(alpha_path, 1), size(alpha_path, 2), n_trajs);
            noises = zeros(size(alpha_path, 1), n_trajs);
            for i = 1:n_trajs
                [noisey_trajs(:, :, i), noises(:, i)]  = obj.noisyTraj(alpha_path, obj.R_inv, noise);
            end
            if obj.debugSTOMP1
                obj.plotNoiseyTrajs(alpha_path, obj.noisey_trajs);
            end
        end
        
        function traj_costs = evalTrajs(obj, trajs)
            traj_costs = zeros(size(trajs, 1), size(trajs, 3));
            for i_trajs = 1:size(trajs,3)
                for i_timestep = 1:size(trajs, 1)
                    traj_costs(i_timestep, i_trajs) = obj.stateCost(trajs(i_timestep, :, i_trajs));
                end
            end
        end
        
        function traj_prob = probTrajs(obj, costs)
            % reducing cost magnitude and clipping
            % so that it doesn't saturate exp
            if mean(costs(:)) > 10
                costs = costs ./ mean(costs(:));
            end
            costs(costs > 10) = 10; 
            lambda = 1/10;
            traj_prob = obj.probTrajs_normsoftmax(costs, lambda);            
        end
                    
        function state_cost = stateCost(obj, q)
            state_cost = obj.eval_state(q);
        end
        
        function path_cost = pathCost(obj, path)
            path_cost = obj.eval_path(path);
        end
        
    end
    
    methods(Static)
        function A = computeA(steps)
            % theta is how many controllable dofs
            % steps is number of steps in trajectory
            N = steps;
            % inbuilt function to make diagonal matrix
            A = full(gallery('tridiag',N,1,-2,1));
            % add row with one at top and bottom
            A = [1, zeros(1,size(A,2)-1); A; zeros(1,size(A,2)-1), 1];
        end
        
        function M = computeM(R_inv, N)
            M = R_inv./max(R_inv)/N;
        end
        
        function [noisy_traj, noise] = noisyTraj(alpha_path, R_inv, noise_amp)
            % generates a single noisy trajectory
            % scale amount of range based on joint movement
            range = abs(max(alpha_path) - min(alpha_path));
            noise = mvnrnd(zeros(1,size(alpha_path,1)), R_inv)';
            noisy_traj = alpha_path + noise .* range*noise_amp;
        end
        
        function [] = plotNoiseyTrajs(alpha_path, noisey_trajs)
            for iq = 1:size(noisey_trajs, 2)
                figure()
                hold on;
                plot(alpha_path(:,iq), 'ro');
                title(sprintf('Joint %d', iq));
                for i = 1:size(noisey_trajs, 3)
                    plot(noisey_trajs(:,iq, i), 'xb');
                end
            end
            hold off
        end
        
        function [] = plotCovariance(R_inv)
            figure();
            hold on;
            for i = 1:size(R_inv,2)
                plot(R_inv(:,i), 'x')
            end
            hold off
        end
            
        function traj_prob = probTrajs_softmax(costs, lambda)
            traj_prob = zeros(size(costs));
            % calculating softmax based on costs
            % higher cost should result in lower probability
            for i_timestep = 1:size(costs, 1)
                for i_trajs = 1:size(costs,2)
%                 min_timestep_cost = 
                    traj_prob(i_timestep, i_trajs) = exp(-1/lambda * costs(i_timestep, i_trajs));
                end
                traj_prob(i_timestep, :) = traj_prob(i_timestep,:) / sum(traj_prob(i_timestep,:));
            end
        end
        
        function traj_prob = probTrajs_normsoftmax(costs, lambda)
            traj_prob = zeros(size(costs));
            h = 1/lambda;
            % calculating softmax based on costs
            % normalizing costs based on range of costs for that timestep
            % higher cost should result in lower probability
            for i_timestep = 1:size(costs, 1)
                min_cost = min(costs(i_timestep,:));
                max_cost = max(costs(i_timestep,:));
                for i_trajs = 1:size(costs,2)
                    cost_norm = (costs(i_timestep, i_trajs) - min_cost)/(max_cost - min_cost);
                    if isnan(cost_norm) % in case of divide by zero
                        cost_norm = 1;
                    end
                    traj_prob(i_timestep, i_trajs) = exp(-h * cost_norm);
                end
                traj_prob(i_timestep, :) = traj_prob(i_timestep,:) / sum(traj_prob(i_timestep,:));
            end
        end
        
        function delta_q = deltaQ(traj_probs, noise, M)
            delta_q_noise = sum(traj_probs .* noise, 2);
            delta_q = M * delta_q_noise;
        end
        
        function path_adj = adjustPath(alpha_path, delta)
            path_adj = alpha_path + delta;
        end
        
    end
end