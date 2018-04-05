function out = groupCheck(g)
% check to convert into group representation if it is not
    if size(g) ~= [4,4]
        out = groupSE3(g);
    else
        out = g;
    end
end