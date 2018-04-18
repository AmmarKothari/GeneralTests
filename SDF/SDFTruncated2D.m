function SDFTruncated2D(fn, truncation_length)
% Same as SDFTruncated but with notion of inside defined
    img = imread(fn);
    gray = rgb2gray(img);
    gray_lim = size(gray);
    inside = ceil(gray_lim/2);
    DF_ratio = 1;
    new_meas_weight = 1;
    DF = 10*ones(ceil(size(gray)/DF_ratio));
    DF_lim = size(DF);
    [DF_posx,DF_posy] = meshgrid(1:DF_ratio:size(gray,1), 1:DF_ratio:size(gray,2));
    DF_weights = zeros(DF_lim);

    % iterating over all possible values in the scene
    for i1 = 1:gray_lim(1)
       for i2 = 1:gray_lim(2)
           % for each point find the closest surface point
           xpos = ceil(i1/DF_ratio);
           ypos = ceil(i2/DF_ratio);
           d = DF(xpos,ypos);
           for j1 = max(i1-truncation_length, 1):min(i1+truncation_length, gray_lim(1))
               for j2 = max(i2-truncation_length, 1):min(i2+truncation_length, gray_lim(2))
                   val = gray(j1,j2);
                   if val < 200
                       d = min(abs(d),sqrt( (j1-i1)^2 + (j2-i2)^2));
                       if norm([i1,i2]-inside) < norm([j1,j2]-inside)
                           d = -d;
                       end
                   end
               end
           end
           DF(xpos,ypos) = d;
       end
        imagesc(DF)
        pause(0.1)
    end
    colormap('hot');
    imagesc(DF)
    colorbar;
end