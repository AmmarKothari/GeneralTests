classdef DiffDrive
    %DiffDrive - differential drive model to define dynamics of robot
    %   Detailed explanation goes here
    
    properties
        % phyiscal
        l=1 % distance between wheels
        dt=1e-3; % how often to update the position.
        vMax = 1; vMin = 0;
        % state
        q = struct('x', 0, 'y', 0, 'theta', 0);
        qd = struct('v', 0, 'w', 0);
        qdd = struct('a', 0, 'alpha', 0);
        qr = struct('x', 0, 'v', 0, 'a', 0);
        ql = struct('x', 0, 'v', 0, 'a', 0);
        
        % record values
        state_all = []
        
    end
    
    methods
        function obj = DiffDrive(l, dt)
            %UNTITLED7 Construct an instance of this class
            %   Detailed explanation goes here
            obj.l = l;
            obj.dt = dt;
        end
        
        function obj = step_dynamics(obj, u)
            %step_dynamics - Move the simulation forward by dt
            %   Detailed explanation goes here
            dt = obj.dt;
            obj.ql.a = u(1);
            obj.qr.a = u(2);
            xL = obj.ql.x; vL = obj.ql.v; aL = obj.ql.a;
            xR = obj.qr.x; vR = obj.qr.v; aR = obj.qr.a;
            x = obj.q.x; y = obj.q.y; theta = obj.q.theta;
            v = obj.qd.v;
            omega = (vR - vL)/obj.l;
            theta = theta + omega * dt;
            % fix wrap around
            theta = obj.fix_wrap_around(theta);
            
            if (vR - vL) == 0
                R = inf; % when it is going straight
            elseif vR == -vL
                R = 0; % spinning in place
            else
                R = obj.l/2 * (vL + vR)/(vR - vL);
            end
            obj.ql.x = xL + vL * dt + 1/2 * aL*dt^2;
            obj.qr.x = xR + vR * dt + 1/2 * aR*dt^2;
            obj.ql.v = vL + aL * dt;
            obj.qr.v = vR + aR * dt;
            v = 1/2 * (obj.ql.v + obj.qr.v);
            v = obj.clampV(v); % speed limits need to be implemented on the wheels -- take from mobile robotics class
            if R ~= inf
                x_ICC = x - R * sin(theta);
                y_ICC = y + R * cos(theta);
                xp = cos(omega*dt) * (x-x_ICC) + -sin(omega*dt) * (y-y_ICC) + x_ICC;
                yp = sin(omega*dt) * (x-x_ICC) + cos(omega*dt) *  (y-y_ICC) + y_ICC;
            else
                xp = x + v * dt * cos(theta);
                yp = y + v * dt * sin(theta);
            end
            obj.q.x = xp; obj.q.y = yp; obj.qd.v  = v; obj.q.theta = theta;

        end
        
        function obj = recordData(obj)
            obj.state_all = [obj.state_all; obj.q.x, obj.q.y, obj.q.theta, obj.qd.v];
        end
        
        function obj = testDynamics(obj)
            points = 5000;
            obj.state_all = [];
            %test 1
            obj.ql.x = 0; obj.ql.v = 0; obj.ql.a = 0;
            obj.qr.x = 0; obj.qr.v = 0; obj.qr.a = 0;
            obj.q.x = 0; obj.q.y = 0; obj.q.theta = pi/4; obj.qd.v = 0;
            state_array = zeros( points, 4);
            state_t = state_array;
            obj.dt = 0.01;
            t = obj.dt:obj.dt:points*obj.dt';
            for i = 1:points
%                 obj = obj.step_dynamics([sin(t(i)), sin(t(i))^2]);
                obj = obj.step_dynamics([0.2, 0.1]);
                obj = obj.recordData();
            end
            obj.plotRecordedState();
        end
        
        function obj = plotRecordedState(obj)
            plot(obj.state_all(:,1), obj.state_all(:,2), 'c*'); %end
            hold on
            plot(obj.state_all(1,1), obj.state_all(1,2), 'ro'); % start point
            plot(obj.state_all(end,1), obj.state_all(end,2), 'go'); % end point
            hold off
            axis equal
        end
            

        function v_clamp = clampV(obj, v)
            v_clamp = sign(v) * min(max(abs(v),obj.vMin), obj.vMax);
        end
    
    end
    methods (Static)
        function theta_fix = fix_wrap_around(theta)
            % keep theta between -pi and pi
            if theta < -pi
                theta_fix = theta + 2*pi;
            elseif theta > pi
                theta_fix = theta - 2*pi;
            else
                theta_fix = theta;
            end
        end
        
    end
end

