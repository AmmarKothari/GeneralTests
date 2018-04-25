% questions from ProbRob chapter 2


% % Problem 2
%                         tomorrow
%                 sunny   cloudy  rainy
% today   sunny     0.8     0.2     0
%         cloudy    0.4     0.4     0.2
%         rainy     0.2     0.6     0.2
probs = [0.8, 0.2, 0;
        0.4, 0.4, 0.2;
        0.2, 0.6, 0.2];

idxs = {'sunny', 'cloudy', 'rainy'};
get_idx = @(x) find(strcmp(idxs, x));
% part a
sequence = {'sunny', 'cloudy', 'cloudy', 'rainy'};
p = 1;
for s = 2:length(sequence)
    p = p*probs(get_idx(sequence{s-1}), get_idx(sequence{s}));
end

% part c
num_days = 10000;
day_idxs = randi(3);
for i=1:num_days
    tot_prob = cumsum(probs(day_idxs(i),:));
    sample = rand(1);
    s = find((tot_prob - sample)>0,1);
    day_idxs = [day_idxs; s];
end
stationary_dist = [sum(day_idxs == 1), sum(day_idxs == 2), sum(day_idxs == 3)]/length(day_idxs)

% part d
A = [probs(1,1)-1, probs(2,1), probs(3,1);
    probs(1,2), probs(2,2)-1, probs(3,2);
%     probs(3,1), probs(3,2), probs(3,3)-1;
    1, 1, 1];
b = [0;0; 1];
stationary_dist_calc = [A\b]'

% part e
entropy = -sum(stationary_dist_calc .* log2(stationary_dist_calc))