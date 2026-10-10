# a4_avg_bound.jl —— 「兜底步统一界」的严格版本
#   命题：ℓ_max ≤ max( τ ,  max_{j} [ (Σ_{i<j} p_i)/4 + p_j ] )     （见下方推导）
#     · 填充步（E_j≠∅）：算法只放能装下的机 ⟹ 该机负载 ≤ τ。
#     · 兜底步（E_j=∅）：算法放"最轻"机 ⟹ 放置前负载 ≤ 已见之和/4。
#     · 每台机的最终负载 = 它最后一次收到工件时的负载 ⟹ 上面两种情形已覆盖。
#   于是：把右边那个 max 在整家族上取最大，若 ≤6/5，则**所有轨迹**一次封底。
#   用法：julia --project=. a4_avg_bound.jl [preds] [pack|nopack]
include("a4_lib.jl")
include("a4_milp10.jl")
using JuMP, HiGHS

function base_model(n::Int, preds::Symbol, pack::Bool)
    if pack
        return _base(n; preds = preds, cuts = false)
    end
    m = Model(HiGHS.Optimizer); set_silent(m)
    @variable(m, P[1:n])
    for i in 1:n; set_lower_bound(P[i], ALP); set_upper_bound(P[i], 1.0); end
    for i in 1:(n-1); @constraint(m, P[i] >= P[i+1]); end
    if preds == :full1
        @constraint(m, P[1] >= P[4] + P[5])
    else
        @constraint(m, P[4] + P[5] >= P[1])
    end
    if preds == :card
        @constraint(m, P[2] <= P[3] + P[4]); @constraint(m, P[3] <= P[4] + P[5]); @constraint(m, P[5] <= P[3])
    end
    @constraint(m, sum(P) <= 4.0)
    return m, P
end

function run(preds::Symbol, pack::Bool, n::Int = 10, tlim::Float64 = 600.0)
    println("── preds=", preds, "  pack=", pack, "  n=", n)
    best = -Inf; bestj = 0
    # ① τ = ρ·(p4+p5)
    m, P = base_model(n, preds, pack); set_time_limit_sec(m, tlim)
    @objective(m, Max, RHO * (P[4] + P[5])); optimize!(m)
    if termination_status(m) == OPTIMAL
        v = objective_value(m)
        println("   τ 项：最大值 = ", round(v, digits = 6), "   见证 p = ", round.(value.(P), digits = 4))
        v > best && (best = v; bestj = -1)
    else
        println("   τ 项：状态 ", termination_status(m))
    end
    # ② (Σ_{i<j} p_i)/4 + p_j
    for j in 5:n
        m, P = base_model(n, preds, pack); set_time_limit_sec(m, tlim)
        @objective(m, Max, sum(P[i] for i in 1:(j-1)) / 4 + P[j]); optimize!(m)
        if termination_status(m) == OPTIMAL
            v = objective_value(m)
            println("   j=", j, "：最大值 = ", round(v, digits = 6), "   见证 p = ", round.(value.(P), digits = 4))
            v > best && (best = v; bestj = j)
        else
            println("   j=", j, "：状态 ", termination_status(m))
        end
    end
    println("   ⟹ 统一界 = ", round(best, digits = 6), "（来自 ", bestj == -1 ? "τ 项" : "j=$bestj", "）")
    return best
end

function main()
    preds = length(ARGS) >= 1 ? Symbol(ARGS[1]) : :card
    pack = length(ARGS) >= 2 ? ARGS[2] == "pack" : true
    n = length(ARGS) >= 3 ? parse(Int, ARGS[3]) : 10
    run(preds, pack, n)
end
abspath(PROGRAM_FILE) == abspath(@__FILE__) && main()
