%% Problem 1
% a
F = @(s) (s+2)*(s+4)/(s*(s+1)*(s+3));
syms s
disp('Laplace Domain: ')
pretty(F(s))
disp('Time Domain: ')
pretty(ilaplace(F(s)))

% b
F = @(n) 3*(n+2) / (n * (n^2 +2*n + 10));
SS_F = @(n) n*3*(n+2) / (n * (n^2 +2*n + 10));
range = logspace(1,-5, 30);
out = 0*range;
for i = 1:length(range)
    out(i) = SS_F(range(i));
end
plot(range, out, 'r-*')

