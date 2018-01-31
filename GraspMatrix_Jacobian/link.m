classdef link
    properties
        length
        pose_world
    end

    methods
        function obj = link(length, pose)
            obj.length = length;
            obj.pose_world = pose;
        end

    end


end