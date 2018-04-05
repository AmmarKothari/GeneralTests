classdef pose_class
    properties
        group, p, q, groupinv
    end
    methods
        function obj = pose_class(g)
            if isa(g, 'pose_class')
                obj.group = g.group;
                obj.groupinv = g.groupinv;
                obj.p = g.p;
                obj.q = g.q;
            else
                obj.group = obj.group_func(g);
                obj.groupinv = obj.group_func(g, 'y');
                obj.p = obj.poseFromMatrix(g);
                obj.q = obj.quatFromMatrix(obj.group);
            end
        end
        
        function [x,y,theta,c,s]=vals(obj)
            x = obj.p(1);
            y = obj.p(2);
            theta = obj.p(3);
            c = cos(theta);
            s = sin(theta);
        end
        
        
        function T = group_func(obj, g, inv) % add support for quaternion + position
            if nargin < 3
                inv = 'n';
            end
            if all(size(g) == [1,6]) || all(size(g) == [6,1])
                x = g(1);
                y = g(2);
                z = g(3);
                gamma = g(4);
                beta = g(5);
                alpha = g(6);
                
                if inv == 'y'
                    T = obj.RotX(-gamma) * obj.RotY(-beta) * obj.RotZ(-alpha) * obj.Tl(-x,-y,-z);
                else
                    T = obj.Tl(x, y, z) * obj.RotZ(alpha) * obj.RotY(beta) * obj.RotX(gamma);
                end
            elseif all(size(g) == [4,4])
                T = g;
            else
                exception = MException('MyFunc:notValidSize', 'Array is not a valid size');
                throw(exception)
            end
        end
        
        function ax = plotPose(obj, ax, p, m, scale) % make this a function in GeoOps folder
            hold_state = ishold(ax);
            hold on
            if nargin < 4
                m = 'ro';
            end
            if nargin < 5
                scale = 0.1;
            end
            if nargin < 3
                p = obj.p;
            end
            % base coordinate system
            x1 = [1;0;0;0;0;0]*scale;
            y1 = [0;1;0;0;0;0]*scale;
            z1 = [0;0;1;0;0;0]*scale;
            x1_moved = obj.poseFromMatrix(leftAction(x1, p));
            y1_moved = obj.poseFromMatrix(leftAction(y1, p));
            z1_moved = obj.poseFromMatrix(leftAction(z1, p));
            
            % % center point of axes
            scatter3(ax, p(1), p(2), p(3), m)
            % x axis
            xQ = obj.plotArrow(ax, p, x1_moved-p, 'r');
            % y axis
            yQ = obj.plotArrow(ax, p, y1_moved-p, 'b');
            % z axis
            zQ = obj.plotArrow(ax, p, z1_moved-p, 'g');
%             if ~hold_state
%                 hold off
%             end
        end
        
    end
    
    methods (Static)
        function g = poseFromMatrix(G)
            if all(size(G) == [4,4])
                x = G(1,4);
                y = G(2,4);
                z = G(3,4);
                try
                    gamma = atan2(G(3,2),G(3,3));
                    alpha = atan2(G(2,1), G(1,1));
                    % second term simplifies to cos(beta)
                    beta = atan2(-G(3,1), G(1,1)*cos(alpha) + G(2,1)*sin(alpha));
                catch
                    disp('Error!')
                end
                g = [x, y, z, gamma, beta, alpha];
            elseif all(size(G) == [1,6]) || all(size(G) == [6,1])
                g = G;
            else
                exception = MException('MyFunc:notValidSize', 'Array is not a valid size');
                throw(exception)
            end
        end
        
        function q = quatFromMatrix(G)
            q = rotm2quat(G(1:3, 1:3));
        end    
        
        function Rx = RotX(gamma)
            % make this a combination of rotx and rotm2tform
            s = sin(gamma);
            c = cos(gamma);
            Rx = [
            1,	0,	0,	0;
            0,	c,	-s,	0;
            0,	s,	c,	0;
            0,	0,	0,	1;
            ];
        end

        function Ry = RotY(beta)
            s = sin(beta);
            c = cos(beta);
            Ry = [
            c,		0,	s,	0;
            0,		1,	0,	0;
            -s,	0,	c,	0;
            0,		0,	0,	1
            ];
        end

        function Rz = RotZ(alpha)
            s = sin(alpha);
            c = cos(alpha);
            Rz = [
            c,	-s,	0,	0;
            s,	c,	0,	0;
            0,	0,	1,	0;
            0,	0,	0,	1;
            ];
        end

        function T = Tl(x,y,z)
            T = [
            1,	0,	0,	x;
            0,	1,	0,	y;
            0,	0,	1,	z;
            0,	0,	0,	1;
            ];
        end

        function Q = plotArrow(a, cosys, pose, c)
            hold on
            Q = quiver3(a, cosys(1), cosys(2), cosys(3), pose(1), pose(2), pose(3), c);
            hold off
        end
    end
end
    
    
    