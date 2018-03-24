classdef PlanarLidarSensor
    %Single Plane LidarSensor
    %   Simulates a set of lasers being emitted and returning if hitting an
    %   object
    
    properties
        bearing, range
    end
    
    methods
        function obj = untitled4(bearing,range)
            %UNTITLED4 Construct an instance of this class
            %   Detailed explanation goes here
            obj.bearing = bearing;
            obj.range = range;
        end
        
        function outputArg = method1(obj,inputArg)
            %METHOD1 Summary of this method goes here
            %   Detailed explanation goes here
            outputArg = obj.Property1 + inputArg;
        end
    end
end

