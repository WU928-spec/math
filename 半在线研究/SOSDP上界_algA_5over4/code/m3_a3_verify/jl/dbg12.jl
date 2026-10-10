using JuMP, HiGHS
m = Model(HiGHS.Optimizer); set_silent(m)
@variable(m, a); @variable(m, b)
for i in 1:4
    (i <= 2) ? @constraint(m, a + b <= 1) : @constraint(m, a + b >= 2)
end

n = 0
for c in all_constraints(m; include_variable_in_set_constraints = false)
    global n += 1; println(n, ": ", c)
end
