# a4_fillz.jl —— 关键 LP：max( ρ(p4+p5) + p_n ) 与 max( ρ(p4+p5) + p_j )（按最后一个收件工件）
#   情形(1,0)：接收机此前收过一次填充 ⟹ L ≤ τ ⟹ 兜底后 ≤ τ + z。所以只需这个值 ≤ 6/5。
include("a4_lib.jl")
include("a4_avg_bound.jl")
using JuMP, HiGHS

function fillz(n::Int, preds::Symbol, tlim = 100.0)
    m, P = base_model(n, preds, true)
    set_time_limit_sec(m, tlim)
    @objective(m, Max, RHO * (P[4] + P[5]) + P[n])
    optimize!(m)
    st = termination_status(m)
    if st == OPTIMAL
        return objective_value(m), value.(P)
    else
        return NaN, Float64[]
    end
end

for (preds, n) in [(:card, 10), (:full45, 10), (:full45, 9), (:full45, 11), (:full45, 12), (:full1, 10), (:full1, 11), (:full1, 12)]
    v, pv = fillz(n, preds)
    println(preds, "  n=", n, "  max(ρ(p4+p5)+p_n) = ", round(v, digits = 6),
            isnan(v) ? "" : "   见证 p = " * string(round.(pv, digits = 4)))
    flush(stdout)
end
