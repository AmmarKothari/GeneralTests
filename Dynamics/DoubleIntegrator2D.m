classdef DoubleIntegrator2D
    properties
        % state is only x,y no orientation
        state_dims = 2;
        q, qd, qdd
        q_all, qd_all, qdd_all
    end
    
    methods
        function obj = DoubleIntegrator2D()
            obj.q=zeros(obj.state_dims,1);
            obj.qd = obj.q;
            obj.qdd = obj.q;
        end
        
        function obj = setState(obj, q, qd, qdd)
            obj.q = q;
            obj.qd = qd;
            obj.qdd = qdd;
        end
        
        function obj = stepDynamics(obj, u, dt)
            acc = obj.qdd + reshape(u, [2,1]);
            obj.q = obj.q + obj.qd*dt + 1/2*dt^2*acc;
            obj.qd = dt*acc;
        end
        
    end
    
    methods (Static)
    end
end