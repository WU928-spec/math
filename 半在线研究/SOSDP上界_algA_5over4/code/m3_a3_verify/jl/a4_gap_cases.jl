# a4_gap_cases.jl —— 按"最后兜底步接收机的收件结构"分情形，分别求 LP 上界
#   情形 (f,b) = 接收机之前收了 f 个填充、b 个兜底（由 6533 条片证实只有 (0,0),(0,1),(1,0)）
#   每情形写出接收机的负载式 + 兜底步"全部不合格"约束 + 装箱，取最大 = 该情形的 LP 上界
#   用法：julia --project=. a4_gap_cases.jl
include("a4_lib.jl")
include("a4_avg_bound.jl")
using JuMP, HiGHS

function case_10(n::Int, jstar::Int, ms::Int, i::Int, preds::Symbol)
    # 情形(1,0)：接收机 m*，第 i 步填了一个件（故 p_ms + p_i ≤ τ），j* 步兜底。
    m, P = base_model(n, preds, true)
    set_time_limit_sec(m, 300.0)
    τ = RHO * (P[4] + P[5])
    S = sum(P[k] for k in 1:(jstar-1))
    L = P[ms] + P[i]
    @constraint(m, L <= τ)                                  # 填充条件
    @constraint(m, L <= S / 4)                              # m* 是最轻机
    @constraint(m, S >= L + 3 * (τ - P[jstar]))             # 其余三台都不合格
    @objective(m, Max, L + P[jstar])                        # 最终负载
    optimize!(m)
    return termination_status(m) == OPTIMAL ? objective_value(m) : NaN
end

function case_00(n::Int, jstar::Int, ms::Int, preds::Symbol)
    # 情形(0,0)：接收机只有初始件
    m, P = base_model(n, preds, true)
    set_time_limit_sec(m, 300.0)
    τ = RHO * (P[4] + P[5]); S = sum(P[k] for k in 1:(jstar-1)); L = P[ms]
    @constraint(m, L <= S / 4); @constraint(m, S >= L + 3 * (τ - P[jstar]))
    @objective(m, Max, L + P[jstar]); optimize!(m)
    return termination_status(m) == OPTIMAL ? objective_value(m) : NaN
end

function case_01(n::Int, jstar::Int, jp::Int, ms::Int, preds::Symbol)
    # 情形(0,1)：接收机第 jp 步收了一个更早的兜底（m* 当时是只有初始件的最轻机），j* 步再兜底
    m, P = base_model(n, preds, true)
    set_time_limit_sec(m, 300.0)
    τ = RHO * (P[4] + P[5])
    Sp = sum(P[k] for k in 1:(jp-1))                        # jp 步前的和
    L = P[ms] + P[jp]                                       # jp 步后接收机的负载
    @constraint(m, Sp >= P[ms] + 3 * (τ - P[jp]))           # jp 步全部不合格
    @constraint(m, P[ms] <= Sp / 4)                         # jp 步时 m* 是最轻（只有初始件）
    S = sum(P[k] for k in 1:(jstar-1))
    @constraint(m, L <= S / 4)                              # j* 步时 m* 仍最轻
    @constraint(m, S >= L + 3 * (τ - P[jstar]))             # j* 步全部不合格
    @objective(m, Max, L + P[jstar]); optimize!(m)
    return termination_status(m) == OPTIMAL ? objective_value(m) : NaN
end

function main()
    n = 10; preds = :card
    println("情形 (1,0)（m*, i, j*）的上确界：")
    b10 = -Inf
    for ms in 1:4, jstar in 6:n, i in 5:(jstar-1)
        v = case_10(n, jstar, ms, i, preds)
        v > b10 && (b10 = v)
    end
    println("   (1,0) max = ", round(b10, digits = 6))
    b00 = -Inf
    for ms in 1:4, jstar in 5:n
        v = case_00(n, jstar, ms, preds); v > b00 && (b00 = v)
    end
    println("   (0,0) max = ", round(b00, digits = 6))
    b01 = -Inf
    for ms in 1:4, jstar in 6:n, jp in 5:(jstar-1)
        v = case_01(n, jstar, jp, ms, preds); v > b01 && (b01 = v)
    end
    println("   (0,1) max = ", round(b01, digits = 6))
    println("⟹ 兜底情形 LP 上界 = max(", round(b10, digits=6), ", ", round(b00, digits=6), ", ", round(b01, digits=6), ")")
    println("   （填充情形 ≤ τ ≤ ", round(1.18, digits=4), " 已封闭）")
end
main()
