function DF = DFTruncated2D(fn, truncation_length)
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
                       d = min(d,sqrt( (j1-i1)^2 + (j2-i2)^2));
%                        fprintf('%d',d)
                   end
               end
           end
           DF(xpos,ypos) = d;
       end
    end
    colormap('hot');
    imagesc(DF)
    colorbar;
end