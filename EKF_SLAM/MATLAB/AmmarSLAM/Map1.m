classdef Map1
    %Map1 - example map with ID landmarks
    %   simple map that will have labelled (named) landmarks that will
    %   define the inside and outisde of the track
    % TODO: more complex maps can load map from an image file
    
    properties
        n_landmarks = 0
        landmarks = []
        world = [100, 100]
    end
    
    methods
        function obj = Map1()
            % all landmarks and names
            %   Detailed explanation goes here
            obj.landmarks = {
                            [10, 10], 'pt1';
                            [10, 50], 'pt2';
                            [50, 50], 'pt3';
                            [50, 10], 'pt4'
                            };
            obj.n_landmarks = size(obj.landmarks,1);
            obj.world = [100, 100];
        end
        
        function [] = plotMap(obj)
            %plotMap - plots the map borders and landmarks
            %   Detailed explanation goes here
            borders = [ 0, 0;
                        obj.world(1), 0;
                        obj.world;
                        0, obj.world(2);
                        0, 0];
            xy = [];
            for i = 1:size(obj.landmarks,1)
                xy = [xy; obj.landmarks{i, 1}];
            end
            plot(xy(:,1), xy(:,2), 'rx');
            hold on;
            plot(borders(:,1), borders(:,2), 'k-')
            hold off
        end
    end
end

