mu = 1;
std = 1;
x = mu-2*std:0.01:mu+2*std;
y = normpdf(x, mu, std);
% for i =1:length(x)
%     p = randn(1);
%     sample = mu + std*p;
%       
%     
%     
% end