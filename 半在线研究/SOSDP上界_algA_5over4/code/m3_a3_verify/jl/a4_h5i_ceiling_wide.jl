# H5i LP 天花板：广覆盖版（多起点 + 随机重启 + 步 5 边界族）
# 目标：尽力找出任何一片 > ρ 的轨迹片；找不到 ⟹ 天花板 = ρ 的证据增强
include("a4_lib.jl")
using JuMP, HiGHS, Printf, Random
const RHO2 = C_TARGET

function h5i_trace(p::Vector{Float64})
    n = length(p); load = zeros(4); assign = zeros(Int, n); branch = fill(:open, n)
    Esets = [Int[] for _ in 1:n]
    for j in 1:min(4, n); assign[j] = j; load[j] += p[j]; end
    n <= 4 && return (assign, branch, :none, argmax(load), maximum(load), Esets)
    lam = (p[4] + p[5]) > p[1] ? :p45 : :p1
    τ = RHO2 * max(p[1], p[4] + p[5])
    lpt = false
    for j in 5:n
        E = [m for m in 1:4 if load[m] + p[j] <= τ + 1e-15]
        Esets[j] = copy(E)
        if isempty(E); assign[j] = argmin(load); branch[j] = :fb
        elseif lpt;  assign[j] = E[argmin(load[E])]; branch[j] = :E_lightest
        else;        assign[j] = E[argmax(load[E])]; branch[j] = :E_fullest end
        j == 5 && assign[j] != 1 && (lpt = true)
        load[assign[j]] += p[j]
    end
    return (assign, branch, lam, argmax(load), maximum(load), Esets)
end

function ceiling_h5i(p0)
    cstar = opt_makespan(p0, 4); p = p0 ./ cstar
    assign, branch, lam, am, ms, Esets = h5i_trace(p)
    best = -Inf; bp = Float64[]
    for blocks in partitions(length(p), 3, 4)
        m = Model(HiGHS.Optimizer); set_silent(m)
        @variable(m, P[1:length(p)] >= 0)
        for i in 1:(length(p) - 1); @constraint(m, P[i] >= P[i+1]); end
        for blk in blocks; @constraint(m, sum(P[i] for i in blk) <= 1.0); end
        if lam == :p1; @constraint(m, P[1] >= P[4] + P[5]); else; @constraint(m, P[4] + P[5] >= P[1]); end
        load = [AffExpr(0.0) for _ in 1:4]
        for j in 1:min(4, length(p)); load[j] += P[j]; end
        τ = RHO2 * (lam == :p1 ? P[1] : P[4] + P[5])
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
    rng = MersenneTwister(99)
    razor = [0.6, 0.5, 0.5, 0.4, 0.4, 0.4, 0.3, 0.3, 0.3, 0.3]
    tight1 = [0.85169331, 0.77061154, 0.76534715, 0.73779483, 0.73081013, 0.68173299, 0.56294794, 0.28128542]
    starts = Vector{Vector{Float64}}()
    # 结构化族：块常值格点（2–3 值，n=6..11）
    for _ in 1:24
        n = rand(rng, 6:11); k = rand(rng, 2:3)
        vals = sort(rand(rng, 2:9, k) ./ 10; rev = true)
        q = Float64[]; while length(q) < n; push!(q, vals[rand(rng, 1:k)]); end
        push!(starts, sort(q; rev = true))
    end
    push!(starts, razor, tight1, [aa, aa, aa, bb, bb, bb, 1/3, 1/3, 1/3])
    # razor 扰动 + tight1 扰动
    for base in (razor, tight1)
        for _ in 1:8
            push!(starts, sort([b0 * (1 + 0.1 * (rand(rng) - 0.5)) for b0 in base]; rev = true))
        end
    end
    best_all = 0.0; bp_all = Float64[]; nstart = 0
    for s in starts
        nstart += 1
        c, p = ceiling_h5i(s)
        if c > best_all + 1e-9
            best_all = c; bp_all = copy(p)
            @printf("start %2d  新纪录 = %.8f（%sρ）  n=%d\n", nstart, c, c > ρ + 1e-6 ? "超 " : "", length(s))
            flush(stdout)
        end
        # 一轮 hop
        c2, p2 = ceiling_h5i(p ./ opt_makespan(p, 4))
        if c2 > best_all + 1e-9
            best_all = c2; bp_all = copy(p2)
            @printf("  hop    新纪录 = %.8f（%sρ）\n", c2, c2 > ρ + 1e-6 ? "超 " : "")
            flush(stdout)
        end
    end
    println("-"^70)
    @printf("** 广覆盖最大片内天花板 = %.8f（ρ=%.8f）  起点数=%d\n", best_all, ρ, nstart)
    @printf("见证实例 p = %s\n", string(round.(bp_all, digits = 6)))
end
main()
