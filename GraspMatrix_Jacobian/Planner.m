classdef Planner
    properties
        step
        path
        gripper
        cost_map
        x_limits
        y_limits
        x_range
        y_range
    end
    methods
        function obj = Planner(gripper)
            obj.gripper = gripper;
        end
        
        function xy_points = xy_path(obj, path)
%             xy_points = zeros(size(path,1), 2);
            xy_points = [];
            for p = 1:size(path,1)
                xy = obj.gripper.calc_poses(path(p,:));
                xy_end_points = xy.endPoints();
                xy_points = [xy_points; xy_end_points(:,1:2)];
            end
        end
        
        function obj = setCostMap(obj, cost_map, x_range, y_range)
            obj.x_range = x_range;
            obj.y_range = y_range;
            obj.x_limits = [max(obj.x_range), min(obj.x_range)];
            obj.y_limits = [max(obj.y_range), min(obj.y_range)];
            obj.cost_map = cost_map;
        end
        
        
        function obj = STOMP(obj, alpha_path)
            % use STOMP to optimize path
            % add noise to each point in path finding a low cost
            % still a large cost for missing the end point
            % in a high degree of freedom, like the WAM
            % there could be a lot of optimization at goal to reduce cost?
            % higher cost correlates to incorporating less noise from that
            % trajectory into final solution
            iters = 10; % number of iterations
            trajs = 10; % number of trajectories at each timestep
            for i_iter = 1:iters
                for i_traj = 1:trajs
                    
                end
            end
            for ia = 1:size(alpha_path,2)
                cost
                
            end
        end
        
        function cost = xyCost(obj, xy_pt)
            % find cost of an endpoint
            [valx1,idx1] = min(abs(obj.x_range - xy_pt(1)));
            [valy1,idy1] = min(abs(obj.y_range - xy_pt(2)));
            cost = obj.cost_map(idx1,idy1);
        end
            
        
        function cost = QCost(obj, q)
            % find cost of a configuration
            xy = obj.gripper.calc_poses(q);
            xy_end_points = xy.endPoints();
            % find closest point in map for each end point
%             [valx1,idx1] = min(abs(obj.x_range - xy_end_points(1,1)));
%             [valx2,idx2] = min(abs(obj.x_range - xy_end_points(2,1)));
%             [valy1,idy1] = min(abs(obj.y_range - xy_end_points(1,2)));
%             [valy2,idy2] = min(abs(obj.y_range - xy_end_points(2,2)));
%             cost = obj.cost_map(idx1,idy1) + obj.cost_map(idx2,idy2);
            cost = obj.xyCost(xy_end_points(1,:)) + obj.xyCost(xy_end_points(2,:));
        end         
        
        function cost = trajQCost(obj, alpha_path)
            % cost of each configuration based on xy cost map
            cost = zeros(size(alpha_path, 1), 1);
            for i = 1:size(alpha_path, 1)
                % cost for configuration
                cost(i) = obj.QCost(alpha_path(i,:));
                % TODO: add high cost for exceeding joint limits
                % TODO: add high cost for any part of link inside of an
                % object
            end
        end
        
        function ep_cost = endPointCost(obj, alpha_path, goal_xy)
            % high cost for not being at goal position
            dist_epsilon = 0.01;
            xy = obj.gripper.calc_poses(alpha_path(end,:));
            xy_end_points = xy.endPoints();
            if vecnorm(xy_end_points(:,1:2) - goal_xy, 2, 2) > dist_epsilon
                ep_cost = 1e3; % some large number
            else
                ep_cost = 0;
            end
        end
            
    end
    
    methods(Static)
        function alpha_points = linearAlphaPath(start_alphas, goal_alphas, pts)
            s = length(start_alphas);
            alpha_points = zeros(pts, s);
            for i = 1:s
                alpha_points(:, i) = linspace(start_alphas(i), goal_alphas(i), pts);
            end
        end
    end
end