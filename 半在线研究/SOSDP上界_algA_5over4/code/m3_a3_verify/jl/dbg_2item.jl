include("a4_lib.jl"); include("a4_avg_bound.jl")
using JuMP, HiGHS
# ≤2 件机器（含初始件 p_m + 一个填充 p_i，填充条件 p_m+p_i ≤ τ）的负载上确界
function twoitem(ms, i, preds, tlim=120.0)
    n=10; m,P = base_model(n, preds, true); set_time_limit_sec(m, tlim)
    τ = preds==:full1 ? RHO*P[1] : RHO*(P[4]+P[5])
    @constraint(m, P[ms] + P[i] <= τ)          # 填充条件
    @objective(m, Max, P[ms] + P[i])
    optimize!(m)
    return termination_status(m)==OPTIMAL ? objective_value(m) : NaN
end
for (ms,i) in [(1,5),(2,5),(3,5),(4,5),(1,6),(1,7),(1,8),(2,6),(3,6),(4,6),(1,9),(1,10)]
    v = twoitem(ms,i,:card)
    println("  p_$ms + p_$i ≤ τ 的最大值 = ", round(v, digits=5))
end
