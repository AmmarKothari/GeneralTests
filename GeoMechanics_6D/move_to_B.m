function p_local = move_to_B(frameB, p)
    % B must be in the same frame as p
    % move by inv(B) to make B the origin
    p_local = pose_class(inv(frameB.group) * p.group);
end
