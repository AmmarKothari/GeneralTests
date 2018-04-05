function out = leftAction(h, g)
    h = groupCheck(h);
    g = groupCheck(g);   
    out = g*h;
end