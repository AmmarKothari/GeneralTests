classdef link
    properties
        l, r, m
        I_cm, I_end
        R_cm_p, R_cm_d
        % CM position
        p_cm=[0,0], a_cm=[0,0], v_cm=[0,0]
        P_CM=[], V_CM=[], A_CM=[]
        % CM rotation
        t_cm=0, alpha_cm=0, w_cm=0
        T_CM=[],ALPHA_CM=[], W_CM=[]
        % joint values
        j=0, w=0, alpha=0
        J=[], W=[], ALPHA=[]
        % end locations
        p_p=[0,0], v_p=[0,0], a_p=[0,0];
        P_P=[], V_P=[], A_P=[]
        p_d=[0,0], v_d=[0,0], a_d=[0,0];
        P_D=[], V_D=[], A_D=[]
        % Forces in FBD
        O_n=0, O_t=0; % in link frame
        O_x=0, O_y=0, % in world frame based on theta
        O_d_x=0, O_d_y=0 % in world frame, distal forces
        O_d_n=0, O_d_t=0; % in link frame, distal forces
        torque=0;
        TORQUE=[];
    end
    methods
        function obj = link(l,m)
            obj.l = l;
            obj.r = l/2;
            obj.m = m;
            obj.I_cm = obj.I_CM(l,m);
            obj.I_end = obj.I_END(l,m);
            obj.R_cm_p = obj.group([-obj.r, 0, 0]);
            obj.R_cm_d = obj.group([obj.r, 0, 0]);
        end
        
        function obj = store_values(obj)
            obj.P_CM = [obj.P_CM; obj.p_cm];
            obj.V_CM = [obj.V_CM; obj.v_cm];
            obj.A_CM = [obj.A_CM; obj.a_cm];
            obj.TORQUE = [obj.TORQUE; obj.torque];
            obj.W = obj.store(obj.W, obj.w);
            obj.J = obj.store(obj.J, obj.j);
            obj.ALPHA = obj.store(obj.ALPHA, obj.alpha);
            
        end
        
        function obj = plot_CM(obj, fig_num)
            cla(figure(fig_num));
            figure(fig_num);
            plot(obj.P_CM(:,1), obj.P_CM(:,2), 'ro')  
%             plot(obj.A_CM(:,1), obj.A_CM(:,2), 'ro')         
        end
        
        function obj = plot_Torque(obj, fig_num)
            figure(fig_num)
            plot(1:length(obj.TORQUE), obj.TORQUE, 'rx')
        end
        
    end
    
    methods (Static)
        function g = group(pose)
            g = [cos(pose(3)), -sin(pose(3)), pose(1);
                 sin(pose(3)), cos(pose(3)), pose(2);
                 0, 0, 1];
        end
        
        function p = pose(group)
            p = [group(1,3), group(2,3), atan2(group(2,1), group(1,1))];
        end
        
        function I = I_CM(l,m)
            I = 1/12 * m *l^2;
        end
        function I = I_END(l,m)
            I = 1/3 * m * l^2;
        end
        function O = store(O, o)
            O = [O;o];
        end
        
    end
    
end