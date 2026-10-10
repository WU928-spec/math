# dc_dff.jl —— direction C 之 DFF/线性证书实验
#
#   失败情形（接收机最后收件 z=p_n 是兜底）的 LP 上界，逐情形 (0,0)/(1,0)/(0,1)、逐 n、逐分支。
#   约束层：
#     L0: 家族（分支、有序、Σp≤4、件∈[4/15,1]）
#     L1: L0 + 计数（p5≤1/2、p9≤1/3）
#     L2: L1 + 鸽笼 C* 线性约束（p4+p5≤1, p5+p6≤1, ..., p7+p8+p9≤1, p8+..+p10≤1, p4+..+p7≤2, ...）【新】
#     L3: L2 + 装箱整数性（MILP，参考值，≈1.2444 那档）
#   填充情形已解析封闭（≤τ≤1.1805）。统一界 1.25 = L1 层的已知值。
#   用法：julia --project=. dc_dff.jl
include("a4_lib.jl")
using JuMP, HiGHS

const RHO = C_TARGET
const ALP = 4.0 / 15.0

"L0/L1/L2 层（纯 LP）或 L3（MILP 带装箱）"
function failure_model(n::Int, preds::Symbol, layer::Int)
    m = Model(HiGHS.Optimizer); set_silent(m)
    @variable(m, P[1:n])
    for i in 1:n; set_lower_bound(P[i], ALP); set_upper_bound(P[i], 1.0); end
    for i in 1:(n-1); @constraint(m, P[i] >= P[i+1]); end
    if preds == :full1
        @constraint(m, P[1] >= P[4] + P[5])
    else
        @constraint(m, P[4] + P[5] >= P[1])
        if preds == :card
            @constraint(m, P[2] <= P[3] + P[4]); @constraint(m, P[3] <= P[4] + P[5]); @constraint(m, P[5] <= P[3])
        end
    end
    @constraint(m, sum(P) <= 4.0)
    if layer >= 1                      # 计数
        @constraint(m, P[5] <= 0.5)
        n >= 9 && @constraint(m, P[9] <= 1.0 / 3.0)
    end
    if layer >= 2                      # 鸽笼 C* 约束（全部有效：某箱必有 k 件 ⟹ 最小 k 件之和 ≤ C*）
        @constraint(m, P[4] + P[5] <= 1.0)
        n >= 6 && @constraint(m, P[5] + P[6] <= 1.0)
        n >= 7 && @constraint(m, P[6] + P[7] <= 1.0)
        n >= 8 && @constraint(m, P[7] + P[8] <= 1.0)
        n >= 9 && @constraint(m, P[7] + P[8] + P[9] <= 1.0)
        n >= 10 && @constraint(m, P[8] + P[9] + P[10] <= 1.0)
        n >= 11 && @constraint(m, P[9] + P[10] + P[11] <= 1.0)
        n >= 12 && @constraint(m, P[10] + P[11] + P[12] <= 1.0)
        @constraint(m, P[4] + P[5] + P[6] + P[7] <= 2.0)   # 前 7 件必有两箱各 ≥2 件
        n >= 8 && @constraint(m, P[5] + P[6] + P[7] + P[8] <= 2.0)
        if n >= 12                                        # 12 件 ⟹ 每箱恰 3 件
            for i in 1:4; @constraint(m, P[i] + P[11] + P[12] <= 1.0); end
        end
    end
    if layer >= 3                      # 装箱（精确）
        @variable(m, x[1:n, 1:4], Bin)
        @variable(m, y[1:n, 1:4])
        for i in 1:n
            @constraint(m, sum(x[i, :]) == 1)
            for b in 1:4
                @constraint(m, y[i, b] <= x[i, b]); @constraint(m, y[i, b] <= P[i])
                @constraint(m, y[i, b] >= P[i] - (1 - x[i, b])); @constraint(m, y[i, b] >= 0)
            end
        end
        for b in 1:4
            @constraint(m, sum(y[i, b] for i in 1:n) <= 1.0)
            @constraint(m, sum(x[i, b] for i in 1:n) <= 3)
        end
        @constraint(m, x[1, 1] == 1)
    end
    return m, P
end

τof(P, preds) = preds == :full1 ? RHO * P[1] : RHO * (P[4] + P[5])

"情形 (1,0)：接收机 m*，第 i 步填充了一件（L=p_m*+p_i≤τ），最后一步 j*=n 兜底"
function case_10(n, i, ms, preds, layer, tlim)
    m, P = failure_model(n, preds, layer); set_time_limit_sec(m, tlim)
    τ = τof(P, preds)
    S = sum(P[k] for k in 1:(n-1))
    L = P[ms] + P[i]
    @constraint(m, L <= τ)
    @constraint(m, L <= S / 4)
    @constraint(m, S >= L + 3 * (τ - P[n]))
    @objective(m, Max, L + P[n])
    optimize!(m)
    return termination_status(m) == OPTIMAL ? objective_value(m) :
           (primal_status(m) == FEASIBLE_POINT ? objective_value(m) : NaN)
end

"情形 (0,0)：接收机只有初始件"
function case_00(n, ms, preds, layer, tlim)
    m, P = failure_model(n, preds, layer); set_time_limit_sec(m, tlim)
    τ = τof(P, preds)
    S = sum(P[k] for k in 1:(n-1))
    L = P[ms]
    @constraint(m, L <= S / 4)
    @constraint(m, S >= L + 3 * (τ - P[n]))
    @objective(m, Max, L + P[n])
    optimize!(m)
    return termination_status(m) == OPTIMAL ? objective_value(m) :
           (primal_status(m) == FEASIBLE_POINT ? objective_value(m) : NaN)
end

"情形 (0,1)：接收机先收过一个兜底（第 jp 步），再收 z"
function case_01(n, jp, ms, preds, layer, tlim)
    m, P = failure_model(n, preds, layer); set_time_limit_sec(m, tlim)
    τ = τof(P, preds)
    Sp = sum(P[k] for k in 1:(jp-1))
    L = P[ms] + P[jp]
    @constraint(m, Sp >= P[ms] + 3 * (τ - P[jp]))
    @constraint(m, P[ms] <= Sp / 4)
    S = sum(P[k] for k in 1:(n-1))
    @constraint(m, L <= S / 4)
    @constraint(m, S >= L + 3 * (τ - P[n]))
    @objective(m, Max, L + P[n])
    optimize!(m)
    return termination_status(m) == OPTIMAL ? objective_value(m) :
           (primal_status(m) == FEASIBLE_POINT ? objective_value(m) : NaN)
end

function run_config(n, preds, layer, tlim)
    vals00 = filter(!isnan, [case_00(n, ms, preds, layer, tlim) for ms in 1:4])
    vals10 = filter(!isnan, [case_10(n, i, ms, preds, layer, tlim) for ms in 1:4 for i in 5:(n-1)])
    vals01 = filter(!isnan, [case_01(n, jp, ms, preds, layer, tlim) for ms in 1:4 for jp in 5:(n-1)])
    b00 = isempty(vals00) ? -Inf : maximum(vals00)
    b10 = isempty(vals10) ? -Inf : maximum(vals10)
    b01 = isempty(vals01) ? -Inf : maximum(vals01)
    b = maximum((b00, b10, b01))
    f(x) = x == -Inf ? "——" : string(round(x, digits=5))
    println("  n=$n preds=$preds layer=$layer : (0,0)=$(f(b00)) (1,0)=$(f(b10)) (0,1)=$(f(b01))  ⟹ $(f(b))   [feasible: $(length(vals00))/$(length(vals10))/$(length(vals01))]")
    flush(stdout)
    return b
end

function main()
    tlim = 120.0
    for n in (10, 11, 12), preds in (:full45, :full1)
        n == 12 && preds == :full1 && continue
        for layer in (0, 1, 2)
            run_config(n, preds, layer, tlim)
        end
    end
    # 参考：L3（带装箱 MILP）只做关键配置
    for (n, preds) in ((10, :full45), (10, :full1), (12, :full45))
        run_config(n, preds, 3, 300.0)
    end
end
abspath(PROGRAM_FILE) == abspath(@__FILE__) && main()
