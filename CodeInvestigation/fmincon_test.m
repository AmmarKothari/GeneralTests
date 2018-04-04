func = @(x) sum(.5*[x(1)^2, x(2)^2-4].^2); % quadratic penalty

r = linspace(-2, 2, 100);
for i1 = 1:length(r)
    for i2 = 1:length(r)
        M(i1,i2) = func([r(i1), r(i2)]);
    end
end
%%

A = [1, 0;
    0, 1];
x0 = [10, 3];
b = [1, 1];
x = fmincon(func, x0, A, b);

%% Super Basic example
func = @(x) abs(x^2 - 9);
x0 = 4;
x = fmincon(func, x0, [], []);

%% Basic example
func = @(x) x^2;
A = 1;
x0 = 4;
b = 1;
x = fmincon(func, x0, A, b);

%% Array example
func = @(x) x(1)^2 + x(2)^2;
A = [1, 0;
    0, 1];
x0 = [10, 3];
b = [1, 1];
x = fmincon(func, x0, A, b);


%% Quadratic Cost
goal = [1, 1];
quad_cost = @(a) 0.5*a^2;
func = @(x) sum([quad_cost(x(1)-goal(1)), quad_cost(x(2)-goal(2))]);
A = [1, 0;
    0, 1];
x0 = [10, 3];
b = [3, 3];
x = fmincon(func, x0, A, b);

%% Bounded Array example
func = @(x) x(1)^2 + x(2)^2;
ub = [1, 2];
lb = [0, 1];
x = fmincon(func, x0, [], [], [], [], lb, ub);

%% Equality Constraint Array example
func = @(x) x(1)^2 + x(2)^2;
Aeq = [1/2, 1];
beq = 1.5;

x = fmincon(func, x0, [], [], Aeq, beq);