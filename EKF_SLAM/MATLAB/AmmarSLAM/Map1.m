classdef Map1
    %Map1 - example map with ID landmarks
    %   simple map that will have labelled (named) landmarks that will
    %   define the inside and outisde of the track
    % TODO: more complex maps can load map from an image file
    
    properties
        n_landmarks = 0;
        landmarks = []
    end
    
    methods
        function obj = Map1()
            % all landmarks and names
            %   Detailed explanation goes here
            obj.landmarks = [0, 10;
                            0, 50;
                            50, 50;
                            50, 10]';
            obj.n_landmarks = size(obj.landmarks,1);
        end
        
        function outputArg = method1(obj,inputArg)
            %METHOD1 Summary of this method goes here
            %   Detailed explanation goes here
            outputArg = obj.Property1 + inputArg;
        end
    end
end

