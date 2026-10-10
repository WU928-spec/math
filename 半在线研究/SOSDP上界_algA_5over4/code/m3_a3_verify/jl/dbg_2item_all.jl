include("a4_lib.jl"); include("a4_avg_bound.jl")
using JuMP, HiGHS
function twoitem(ms, i, preds, tlim=120.0)
    n=10; m,P = base_model(n, preds, true); set_time_limit_sec(m, tlim)
    τ = preds==:full1 ? RHO*P[1] : RHO*(P[4]+P[5])
    @constraint(m, P[ms] + P[i] <= τ)
    @objective(m, Max, P[ms] + P[i]); optimize!(m)
    return termination_status(m)==OPTIMAL ? objective_value(m) : NaN
end
function run()
println("不含 p1 的 ≤2 件机（p_m + p_i ≤ τ）的最大负载：")
worst = -Inf; worstpair = (0,0)
for ms in 2:4, i in 5:10
    v = twoitem(ms, i, :card)
    v > worst && (worst = v; worstpair = (ms,i))
    print(round(v, digits=4), "\t")
end
println("\n⟹ 最大 = ", round(worst, digits=6), " 于 (m,i) = ", worstpair, "   (C* = 1.0)")
end
run()
