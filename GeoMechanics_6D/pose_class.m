classdef pose_class
    properties
        group, p, q
    end
    methods
        function obj = pose_class(g)
            if isa(g, 'pose_class')
                obj.group = g.group;
                obj.p = g.p;
                obj.q = g.q;
            else
                obj.group = obj.group_func(g);
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
        
        
        function T = group_func(obj, g, inv)
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

                Rx = obj.RotX(gamma);
                Ry = obj.RotY(beta);
                Rz = obj.RotZ(alpha);
                t = obj.Tl(x, y, z);
                if inv == 'y'
                    T = RotX(-gamma) * RotY(-beta) * RotZ(-alpha) * Tl(-x,-y,-z);
                else
                    T = t * Rz * Ry * Rx;
                end
            elseif all(size(g) == [4,4])
                T = g;
            else
                exception = MException('MyFunc:notValidSize', 'Array is not a valid size');
                throw(exception)
            end
        end
        
    end
    
    methods (Static)
        function g = poseFromMatrix(G)
            if all(size(G) == [4,4])
                x = group(1,4);
                y = group(2,4);
                z = group(3,4);
                try
                    gamma = atan2(group(3,2),group(3,3));
                    alpha = atan2(group(2,1), group(1,1));
                    % second term simplifies to cos(beta)
                    beta = atan2(-group(3,1), group(1,1)*cos(alpha) + group(2,1)*sin(alpha));
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




    end
end
    
    
    