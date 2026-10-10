# a4_gap_fast.jl —— 无装箱（纯 LP）版：各情形的极端点，超快
#   无装箱 ⟹ 可行集更大 ⟹ 上界更松，但**仍是合法上界**；若它也 ≤1.2 则更强地成立。
include("a4_lib.jl")
include("a4_avg_bound.jl")
using JuMP, HiGHS

function case_lp(n, jstar, ms, i, preds; kind, tlim = 60.0)
    m, P = base_model(n, preds, false)         # 无装箱：纯 LP
    # 加可装箱的必要条件（比全装箱弱得多，但比"Σ≤4"强；全部线性、便宜）
    n >= 5 && @constraint(m, P[5] <= 0.5)                    # >1/2 的件 ≤4
    n >= 9 && @constraint(m, P[9] <= 1.0/3.0)                # >1/3 的件 ≤8
    n >= 5 && @constraint(m, sum(P[i] for i in 1:4) + P[5] <= 4 - (n - 5) * ALP)
    set_time_limit_sec(m, tlim)
    τ = RHO * (P[4] + P[5])
    S = sum(P[k] for k in 1:(jstar-1))
    if kind == :c10                            # (1,0)：接收机 m*，i 步填了一个件
        L = P[ms] + P[i]
        @constraint(m, L <= τ)
    elseif kind == :c00                        # (0,0)：只有初始件
        L = P[ms]
    else                                       # (0,1)：之前收过一个兜底 jp=i
        L = P[ms] + P[i]
        Sp = sum(P[k] for k in 1:(i-1))
        @constraint(m, Sp >= P[ms] + 3 * (τ - P[i]))
        @constraint(m, P[ms] <= Sp / 4)
    end
    @constraint(m, L <= S / 4)
    @constraint(m, S >= L + 3 * (τ - P[jstar]))
    @objective(m, Max, L + P[jstar])
    optimize!(m)
    return termination_status(m) == OPTIMAL ? objective_value(m) : NaN
end

function main()
    n = 10; preds = :card
    println("无装箱纯 LP 松弛，各情形极端点的上界：")
    println("  (1,0) m*=1,i=5,j*=10 : ", round(case_lp(n,10,1,5,preds; kind=:c10), digits=6))
    println("  (0,0) m*=1,j*=10     : ", round(case_lp(n,10,1,5,preds; kind=:c00), digits=6))
    println("  (0,1) m*=1,i=5,j*=10 : ", round(case_lp(n,10,1,5,preds; kind=:c01), digits=6))
end
main()
