# H5i 的 LP 片内天花板（轨迹跳跃搜索版）
# H5i 规则：ρ 线；步 5 fullest-eligible；若步 5 落点 ≠ M1 ⟹ 步 6 起切 lightest-eligible；兜底 argmin 不变。
# LP 编码：eligibility（pre[m]+P[j] ≤/≥ τ）+ 选择不等式（fullest: pre[a]≥pre[m]；lightest: pre[a]≤pre[m]，∀m∈E）+ 装箱划分枚举 + Λ 分支。
include("a4_lib.jl")
using JuMP, HiGHS, Printf
const RHO2 = C_TARGET

"H5i 轨迹：记录每件的落点、E 集、分支类型（:E_fullest / :E_lightest / :fb）、Λ 分支"
function h5i_trace(p::Vector{Float64})
    n = length(p); load = zeros(4); assign = zeros(Int, n); branch = fill(:open, n)
    Esets = [Int[] for _ in 1:n]
    for j in 1:min(4, n); assign[j] = j; load[j] += p[j]; end
    n <= 4 && return (assign, branch, :none, argmax(load), maximum(load), Esets)
    Λ1 = p[1]; Λ2 = p[4] + p[5]
    lam = Λ2 > Λ1 ? :p45 : :p1
    τ = RHO2 * max(Λ1, Λ2)
    lpt = false
    for j in 5:n
        E = [m for m in 1:4 if load[m] + p[j] <= τ + 1e-15]
        Esets[j] = copy(E)
        if isempty(E)
            assign[j] = argmin(load); branch[j] = :fb
        elseif lpt
            assign[j] = E[argmin(load[E])]; branch[j] = :E_lightest
        else
            assign[j] = E[argmax(load[E])]; branch[j] = :E_fullest
        end
        j == 5 && assign[j] != 1 && (lpt = true)
        load[assign[j]] += p[j]
    end
    return (assign, branch, lam, argmax(load), maximum(load), Esets)
end

function ceiling_h5i(p0; rho = RHO2, verbose = true)
    cstar = opt_makespan(p0, 4); p = p0 ./ cstar
    assign, branch, lam, am, ms, Esets = h5i_trace(p)
    if verbose
        println("轨迹：落点=", assign, "  分支=", join(string.(branch), ","), "  Λ=", lam,
                "  最重机=", am, "  H5i makespan（归一化）=", round(ms, digits = 6))
    end
    best = -Inf; bp = Float64[]
    for blocks in partitions(length(p), 3, 4)
        m = Model(HiGHS.Optimizer); set_silent(m)
        @variable(m, P[1:length(p)] >= 0)
        for i in 1:(length(p) - 1); @constraint(m, P[i] >= P[i+1]); end
        for blk in blocks; @constraint(m, sum(P[i] for i in blk) <= 1.0); end
        if lam == :p1; @constraint(m, P[1] >= P[4] + P[5]); else; @constraint(m, P[4] + P[5] >= P[1]); end
        load = [AffExpr(0.0) for _ in 1:4]
        for j in 1:min(4, length(p)); load[j] += P[j]; end
        τ = rho * (lam == :p1 ? P[1] : P[4] + P[5])
        for j in 5:length(p)
            pre = copy(load); a = assign[j]; Ej = Esets[j]
            for mm in 1:4
                if mm in Ej; @constraint(m, pre[mm] + P[j] <= τ)
                else;        @constraint(m, pre[mm] + P[j] >= τ); end
            end
            if isempty(Ej)
                for mm in 1:4; @constraint(m, pre[a] <= pre[mm]); end
            elseif branch[j] == :E_lightest
                for mm in Ej; @constraint(m, pre[a] <= pre[mm]); end
            else
                for mm in Ej; @constraint(m, pre[a] >= pre[mm]); end
            end
            load[a] += P[j]
        end
        for mm in 1:4; @constraint(m, load[am] >= load[mm]); end
        @objective(m, Max, load[am]); optimize!(m)
        if termination_status(m) == OPTIMAL && objective_value(m) > best + 1e-12
            best = objective_value(m); bp = value.(P)
        end
    end
    return best, bp
end

function main()
    ρ = C_TARGET; bb = 1 / (2ρ); aa = 1 - bb
    starts = [
        [0.6, 0.5, 0.5, 0.4, 0.4, 0.4, 0.3, 0.3, 0.3, 0.3],                                  # razor
        [0.85169331, 0.77061154, 0.76534715, 0.73779483, 0.73081013, 0.68173299, 0.56294794, 0.28128542],  # H5i 采样紧实例
        [aa, aa, aa, bb, bb, bb, 1/3, 1/3, 1/3],                                              # ρ 族端点
        [0.59327, 0.5, 0.5, 0.44039, 0.40673, 0.40673, 0.31346, 0.2798, 0.2798, 0.2798],      # 分支 B 最差
        [0.5, 0.5, 0.4, 0.4, 0.4, 0.4, 0.3, 0.3, 0.3],                                        # V1 死
        [0.5, 0.5, 0.5, 0.4, 0.4, 0.4, 0.3, 0.3, 0.3],                                        # H1 死
    ]
    best_all = 0.0; best_p = Float64[]
    for (i, s) in enumerate(starts)
        c, p = ceiling_h5i(s)
        @printf("start %d  片内天花板 = %.6f（=%.4f×ρ）\n", i, c, c / ρ)
        c > best_all && (best_all = c; best_p = copy(p))
    end
    for it in 1:4
        c, p = ceiling_h5i(best_p ./ opt_makespan(best_p, 4))
        @printf("hop %d  片内天花板 = %.6f（=%.4f×ρ）\n", it, c, c / ρ)
        c > best_all + 1e-9 ? (best_all = c; best_p = copy(p)) : break
    end
    println("-"^70)
    @printf("** H5i 最大片内天花板 = %.8f（ρ=%.8f，6/5=1.2）\n", best_all, ρ)
    @printf("对应实例 p = %s\n", string(round.(best_p, digits = 6)))
    # 直接仿真复核
    mk = begin
        p = best_p; n = length(p); load = copy(p[1:min(4, n)])
        Λ = max(p[1], p[4] + p[5]); τ = ρ * Λ; lpt = false
        for j in 5:n
            E = [m for m in 1:4 if load[m] + p[j] <= τ + 1e-15]
            mm = isempty(E) ? argmin(load) : (lpt ? E[argmin(load[E])] : E[argmax(load[E])])
            j == 5 && mm != 1 && (lpt = true)
            load[mm] += p[j]
        end
        maximum(load)
    end
    @printf("该实例上 H5i 直接仿真比值 = %.8f\n", mk / opt_makespan(best_p, 4))
end
main()
