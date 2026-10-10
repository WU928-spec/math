include("a4_lib.jl"); include("a4_avg_bound.jl")
using JuMP, HiGHS
# 情形(1,0) 极端点：m*=1, i=5, j*=10，带装箱，限时 100 s
n=10; preds=:card
m, P = base_model(n, preds, true); set_time_limit_sec(m, 100.0)
τ = RHO*(P[4]+P[5]); S = sum(P[k] for k in 1:9)
L = P[1] + P[5]
@constraint(m, L <= τ); @constraint(m, L <= S/4); @constraint(m, S >= L + 3*(τ - P[10]))
@objective(m, Max, L + P[10]); optimize!(m)
println("状态 = ", termination_status(m), "  上界 = ", (termination_status(m)==OPTIMAL ? round(objective_value(m),digits=6) : NaN))
