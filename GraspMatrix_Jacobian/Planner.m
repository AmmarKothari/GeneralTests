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
        
        function obj = costMap(obj)
            obj.x_limits = [0 10];
            obj.y_limits = [0, 7];
            step_size = 0.1;
            obj.x_range = obj.x_limits(1):step_size:obj.x_limits(2);
            obj.y_range = obj.y_limits(1):step_size:obj.y_limits(2);
            xy_grid = meshgrid(obj.x_range, obj.y_range);
            obj.cost_map = zeros(size(xy_grid));
            for i1 = 1:length(obj.x_range)
                for i2 = 1:length(obj.y_range)
                    obj.cost_map(i1,i2) = 1;
                end
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