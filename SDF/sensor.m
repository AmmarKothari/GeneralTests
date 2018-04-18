function sensor(start_pt, img)
% returns what would be "sensed"
% img is an image of the "object" (2D where object is filled with black
% pixels)
theta = 0;
[rows,cols] = size(img);
e=ones(1,rows*cols);
[X,Y,Z]=ndgrid((1:rows),  (1:cols), 0);
Coords=[X(:),Y(:),Z(:)].';
linedir=[cosd(theta), sind(theta),0].';
DistLessThan1=sum(cross(Coords,linedir*e).^2)<=1 ;

end