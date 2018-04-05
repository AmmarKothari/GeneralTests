function p_local = move_from_A_to_B(frameA, frameB, p)
    % assume world frame is at 0,0,0,0,0,0 -- so don't need to do that
    % transform
    
    % move both to origin and find pose
    % frameB to origin is just the multiple it by the inverse which leads
    % to 0s
    p_local = pose_class(frameB.groupinv * p.group);

end
