function DFTruncated2D(fn)
% as though you could sample every pixel for its location in world
% coordinates
% a surface with thickness is like noisy measurements
% only a distance function because the distance from a surface is the value
% at that point
% there is no notion of viewpoint here so hard to do a sign.
% i could define the inside of the object a priori.
    img = imread(fn);
    gray = rgb2gray(img);
    gray_lim = size(gray);
    DF_ratio = 1;
    truncation_length = 10;
    new_meas_weight = 1;
    DF = zeros(ceil(size(gray)/DF_ratio));
    DF_lim = size(DF);
    [DF_posx,DF_posy] = meshgrid(1:DF_ratio:size(gray,1), 1:DF_ratio:size(gray,2));
    DF_weights = zeros(DF_lim);

    % iterating over all possible values in the scene
    for i1 = 1:gray_lim(1)
       for i2 = 1:gray_lim(2)
           % measurement
           val = gray(i1,i2);
           if val > 200
               xpos = ceil(i1/DF_ratio);
               ypos = ceil(i2/DF_ratio);
               % update in that area
               for j1 = max(xpos-truncation_length, 1):min(xpos+truncation_length, DF_lim(1))
                   for j2 = max(ypos-truncation_length, 1):min(ypos+truncation_length, DF_lim(2))
                       d = sqrt((j1-xpos)^2 + (j2-ypos)^2); % distance from surface
                       DF(j1,j2) = (DF(j1,j2)*DF_weights(j1,j2) + new_meas_weight*d)/(DF_weights(j1,j2)+new_meas_weight);
                       DF_weights(j1,j2) = DF_weights(j1,j2) + new_meas_weight;
                   end
               end
               DF(xpos, ypos) = 0;
           end

       end
    end

    colormap('hot');
    imagesc(DF)
    colorbar;


end