# a4_gap4.jl —— 啃那 4%：兜底步接收机的"精化上界"能否顶到 6/5
#
#   记：某台机最终负载 = 其最后收件时刻的负载。
#   填充：≤ τ ≤ ρ·C* < 6/5·C* ✓（已封闭）。
#   兜底（步骤 j）：接收机是"最轻"，设其放置前负载 = L。LP 变量取 (p, L)，约束：
#     L ≤ S_j/4          （最轻 ≤ 平均）
#     L ≤ S_j - 3(τ - p_j)  （其余三台都 ≥ τ - p_j，因都不合格）
#     L ≤ τ - (j=5? ...)    （B1：接收机的最后收件是"填充" ⟹ L ≤ τ）
#   分别考察 (a) 不带 B1 的松弛；(b) B1（L ≤ τ）两种。
include("a4_lib.jl")
include("a4_avg_bound.jl")
using JuMP, HiGHS

function lp_gap(n::Int, j::Int, preds::Symbol, withB1::Bool)
    m, P = base_model(n, preds, true)
    set_time_limit_sec(m, 300.0)
    @variable(m, L)
    S = sum(P[i] for i in 1:(j-1))
    τ = RHO * (P[4] + P[5])
    @constraint(m, L <= S / 4)
    @constraint(m, L <= S - 3 * (τ - P[j]))
    @constraint(m, L >= P[j])              # 接收机的初始件 ≥ p_j 太松，但 L ≥ 其首个件 ≥ p_n…先放最弱
    withB1 && @constraint(m, L <= τ)
    @objective(m, Max, L + P[j])
    optimize!(m)
    return termination_status(m) == OPTIMAL ? (objective_value(m), value.(P)) : (NaN, Float64[])
end

function main()
    n = 10; preds = :card
    for j in 5:n
        v0, _ = lp_gap(n, j, preds, false)
        v1, _ = lp_gap(n, j, preds, true)
        println("j=", j, "：松弛(无B1) = ", round(v0, digits = 6), "   B1(L≤τ) = ", round(v1, digits = 6))
    end
end
main()
