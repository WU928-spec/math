# a4_lp_ceiling.jl —— A4c 的"轨迹片内 LP 天花板"
#
# 思想：A4c 的行为由 p 决定；给定一个实例，它的轨迹（每个工件落到哪台机、走的是
#   "cap 内 best-fit"还是"兜底最轻机"、Λ 取 p1 还是 p4+p5、最终哪台最重）是确定的。
#   把这些**离散选择固定**后，makespan 在 p 上是线性的，于是可以
#       maximize  ℓ_{argmax}   s.t.  "存在 4 台机器、每台负载 ≤1 的装箱"（枚举所有装箱），
#                                  单调性、轨迹的分支不等式、
#   求该轨迹片内所有实例的最大 makespan。由于 C* ≤ 1 且比值尺度不变，这个最大值就是
#   该轨迹片能达到的竞争比上界。
# 用法：julia --project=. a4_lp_ceiling.jl
include("a4_lib.jl")
using JuMP, HiGHS

const RHO_ALG = C_TARGET          # A4c 用的是竞争比 c 作为 cap 倍率

"记录 A4c 在实例 p 上的轨迹"
function a4c_trace(p::Vector{Float64})
    n = length(p); load = zeros(4); assign = zeros(Int, n); branch = fill(:open, n)
    Esets = [Int[] for _ in 1:n]
    for j in 1:min(4, n)
        assign[j] = j; load[j] += p[j]
    end
    n <= 4 && return (assign, branch, :none, argmax(load), maximum(load))
    Λ1 = p[1]; Λ2 = p[4] + p[5]
    lam = Λ2 > Λ1 ? :p45 : :p1
    τ = RHO_ALG * max(Λ1, Λ2)
    for j in 5:n
        E = [m for m in 1:4 if load[m] + p[j] <= τ + 1e-15]
        Esets[j] = copy(E)
        if isempty(E)
            assign[j] = argmin(load); branch[j] = :fb
        else
            assign[j] = E[argmax(load[E])]; branch[j] = :E
        end
        load[assign[j]] += p[j]
    end
    return (assign, branch, lam, argmax(load), maximum(load), Esets)
end

"给定轨迹，对每个装箱解一个 LP，返回 (最大 makespan, 见证 p, 最优装箱)"
function lp_ceiling(p0::Vector{Float64}; rho_alg = RHO_ALG, verbose = false)
    cstar0 = opt_makespan(p0, 4)
    p = p0 ./ cstar0                      # 归一化到 C* <= 1（尺度不变：轨迹与比值不变）
    n = length(p); assign, branch, lam, argmax_m, ms, Esets = a4c_trace(p)
    println("轨迹：落点=", assign, "  分支=", join(string.(branch), ","), "  Λ=", lam,
            "  最重机=", argmax_m, "  归一化后 A4c makespan = ", round(ms, digits = 6))
    parts = partitions(n, 3, 4)
    best = -Inf; bp = Float64[]; bb = nothing
    for blocks in parts
        model = Model(HiGHS.Optimizer); set_silent(model)
        @variable(model, P[1:n] >= 0)
        for i in 1:(n-1); @constraint(model, P[i] >= P[i+1]); end
        for blk in blocks
            @constraint(model, sum(P[i] for i in blk) <= 1.0)
        end
        # Λ 取值分支
        if lam == :p1
            @constraint(model, P[1] >= P[4] + P[5])
        else
            @constraint(model, P[4] + P[5] >= P[1])
        end
        # 各机负载（含开局）
        load = [AffExpr(0.0) for _ in 1:4]
        for j in 1:min(4, n); load[j] += P[j]; end
        τ = rho_alg * (lam == :p1 ? P[1] : P[4] + P[5])
        for j in 5:n
            pre = copy(load)                       # 放 p_j 之前的负载
            a = assign[j]; Ej = Esets[j]
            for m in 1:4
                if m in Ej
                    @constraint(model, pre[m] + P[j] <= τ)      # m 在 cap 内（E 的定义）
                else
                    @constraint(model, pre[m] + P[j] >= τ)      # m 放不下（闭化）
                end
            end
            if isempty(Ej)
                for m in 1:4
                    @constraint(model, pre[a] <= pre[m])        # a 是最轻机（argmin）
                end
            else
                for m in Ej
                    @constraint(model, pre[a] >= pre[m])        # a 是 E 内最满者（argmax）
                end
            end
            load[a] += P[j]
        end
        for m in 1:4
            @constraint(model, load[argmax_m] >= load[m])
        end
        @objective(model, Max, load[argmax_m])
        optimize!(model)
        if termination_status(model) == OPTIMAL
            v = objective_value(model)
            if v > best + 1e-12
                best = v; bp = value.(P); bb = blocks
            end
        end
    end
    return best, bp, bb, (assign, branch, lam, argmax_m)
end

# 攻击找到的 A4c 最坏实例（n=10，两级形状）
worst = [0.7759, 0.6534, 0.6534, 0.5212, 0.5184, 0.5184, 0.3966, 0.3957, 0.3932, 0.3908]
ms_attack = a4c_trace(worst)[5] / opt_makespan(worst, 4)
println("攻击最坏实例：A4c/OPT = ", round(ms_attack, digits = 6), "   (C* = ",
        round(opt_makespan(worst, 4), digits = 6), ")")
println("-"^84)
ce, cp, bb, tr = lp_ceiling(worst)
println("-"^84)
println("该轨迹片的 LP 天花板（makespan 上确界，C*≤1） = ", round(ce, digits = 6))
println("  = ", round(ce / C_TARGET, digits = 4), " ×c ； ", round(ce / 1.25, digits = 4), " ×(5/4)")
println("  相对目标：6/5=", round(1.2 - ce, digits = 5), "（正=低于 6/5）；29/24=", round(29/24 - ce, digits = 5))
println("  片内最优实例 p = ", round.(cp, digits = 4))
println("  最优装箱 = ", bb)
