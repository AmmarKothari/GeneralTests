function SDFTruncated2D(fn)
% Same as SDFTruncated but with notion of inside defined
    img = imread(fn);
    gray = rgb2gray(img);
    gray_lim = size(gray);
    % inside is closer to middle of image
    inside = ceil(size(gray)/2);
    SDF_ratio = 1;
    truncation_length = 10;
    new_meas_weight = 1;
    SDF = zeros(ceil(size(gray)/SDF_ratio));
    SDF_lim = size(SDF);
    [SDF_posx,SDF_posy] = meshgrid(1:SDF_ratio:size(gray,1), 1:SDF_ratio:size(gray,2));
    SDF_weights = zeros(SDF_lim);
    weight_limit = 75;

    % iterating over all possible values in the scene
    for i1 = 1:gray_lim(1)
       for i2 = 1:gray_lim(2)
           % measurement
           val = gray(i1,i2);
           if val > 200
               xpos = ceil(i1/SDF_ratio);
               ypos = ceil(i2/SDF_ratio);
               % update in that area
               for j1 = max(xpos-truncation_length, 1):min(xpos+truncation_length, SDF_lim(1))
                   for j2 = max(ypos-truncation_length, 1):min(ypos+truncation_length, SDF_lim(2))
                       d = sqrt((j1-xpos)^2 + (j2-ypos)^2); % distance from surface
                       if norm([xpos,ypos]-inside) > norm([j1,j2]-inside)
                          d = -d;                            
                       end
                       SDF(j1,j2) = (SDF(j1,j2)*SDF_weights(j1,j2) + new_meas_weight*d)/(SDF_weights(j1,j2)+new_meas_weight);
                       SDF_weights(j1,j2) = SDF_weights(j1,j2) + new_meas_weight;
                       SDF_weights(j1,j2) = min(weight_limit, SDF_weights(j1,j2));
                   end
               end
               SDF(xpos, ypos) = 0;
           end

       end
    end

    colormap('hot');
    imagesc(SDF)
    colorbar;


end