function T = groupSE3(pose, inv)
    if nargin < 2
        inv = 'n';
    end
    x = pose(1);
    y = pose(2);
    z = pose(3);
    gamma = pose(4);
    beta = pose(5);
    alpha = pose(6);
    
	Rx = RotX(gamma);
	Ry = RotY(beta);
	Rz = RotZ(alpha);
	t = Tl(x, y, z);
    if inv == 'y'
        % this is the version from Murray Li and Sastry
        % weirdness happens when alpha = pi/2
%         R = Rz * Ry * Rx;
%         p = -R.'*[x;y;z;-1];
%         T = R.';
%         T(:,4) = p;
        T = RotX(-gamma) * RotY(-beta) * RotZ(-alpha) * Tl(-x,-y,-z);
    else
        T = t * Rz * Ry * Rx;
    end
end

function Rx = RotX(gamma)
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




