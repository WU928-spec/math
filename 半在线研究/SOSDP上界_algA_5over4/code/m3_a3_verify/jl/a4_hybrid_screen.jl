# 混合/触发规则筛查：有没有一致 <6/5 的候选？
# V4: (6/5)Λ线+fullest；H1: 喂掉队机（min 落后次轻 >10% 且合格时喂 min）；H2: 大小分极（p_j>Λ/3 fullest 否则 lightest）；H7: fullest 但跳过 ≥2 件机
include("/Users/a123456/math/半在线研究/SOSDP上界_algA_5over4/code/m3_a3_verify/jl/a4_lib.jl")
using Random, Printf

function simH(p, kind::Symbol)
    n = length(p); load = copy(p[1:min(4, n)]); cnt = ones(Int, min(4, n))
    n <= 4 && return maximum(load)
    Λ0 = max(p[1], p[4] + p[5])
    τ = (kind == :V4 ? 6 / 5 : C_TARGET) * Λ0
    for j in 5:n
        E = [m for m in 1:4 if load[m] + p[j] <= τ + 1e-15]
        m = if isempty(E)
            argmin(load)
        elseif kind == :H1          # 喂掉队机
            srt = sortperm(load); m1, m2 = srt[1], srt[2]
            (load[m1] < 0.9 * load[m2] && m1 in E) ? m1 : E[argmax(load[E])]
        elseif kind == :H2          # 大小分极
            p[j] > Λ0 / 3 ? E[argmax(load[E])] : E[argmin(load[E])]
        elseif kind == :H7          # 限集中：跳过 ≥2 件机
            E2 = [m for m in E if cnt[m] <= 1]
            isempty(E2) ? E[argmax(load[E])] : E2[argmax(load[E2])]
        else                        # V4 与默认
            E[argmax(load[E])]
        end
        load[m] += p[j]; cnt[m] += 1
    end
    return maximum(load)
end

function main()
    rng = MersenneTwister(42)
    razor = [0.6, 0.5, 0.5, 0.4, 0.4, 0.4, 0.3, 0.3, 0.3, 0.3]
    ρ = C_TARGET; bb = 1 / (2ρ); aa = 1 - bb
    rhofam = [aa, aa, aa, bb, bb, bb, 1/3, 1/3, 1/3]
    branchB = [0.59327, 0.5, 0.5, 0.44039, 0.40673, 0.40673, 0.31346, 0.2798, 0.2798, 0.2798]
    v1fail = [0.5, 0.5, 0.4, 0.4, 0.4, 0.4, 0.3, 0.3, 0.3]
    Ks = [:V4, :H1, :H2, :H7]
    worst = Dict(k => (-Inf, Float64[]) for k in Ks)
    N = 150_000
    for it in 1:N
        fam = rand(rng, 1:7)
        p = if fam <= 2
            n = rand(rng, 5:12); k = rand(rng, 2:4)
            vals = sort(rand(rng, 2:9, k) ./ 10; rev = true)
            q = Float64[]; while length(q) < n; push!(q, vals[rand(rng, 1:k)]); end
            sort(q; rev = true)
        elseif fam == 3
            sort([b0 * (1 + 0.08 * (rand(rng) - 0.5)) for b0 in razor]; rev = true)
        elseif fam == 4
            sort([b0 * (1 + 0.08 * (rand(rng) - 0.5)) for b0 in rhofam]; rev = true)
        elseif fam == 5
            sort([b0 * (1 + 0.08 * (rand(rng) - 0.5)) for b0 in branchB]; rev = true)
        elseif fam == 6
            sort([b0 * (1 + 0.08 * (rand(rng) - 0.5)) for b0 in v1fail]; rev = true)
        else
            n = rand(rng, 5:12); sort(0.25 .+ 0.75 .* rand(rng, n); rev = true)
        end
        cs = opt_makespan(p, 4)
        for k in Ks
            r = simH(p, k) / cs
            if r > worst[k][1]; worst[k] = (r, p); end
        end
    end
    println("混合规则筛查（", N, " 实例）")
    for k in Ks
        r, p = worst[k]
        @printf("%s  攻击最坏=%.6f  n=%2d  实例=%s\n", k, r, length(p), string(round.(p, digits=4)))
    end
end
main()
