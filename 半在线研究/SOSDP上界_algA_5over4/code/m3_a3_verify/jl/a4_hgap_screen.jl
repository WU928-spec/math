# H-gap 正式筛查：ρ 线；p1>p2 → 最轻合格（spread）；否则 → 最满合格（fullest）
# 150k 对抗采样：块常值格点 + 全部历史死亡点扰动 + 平滑随机
include("/Users/a123456/math/半在线研究/SOSDP上界_algA_5over4/code/m3_a3_verify/jl/a4_lib.jl")
using Random, Printf

function simHgap(p)
    n = length(p); load = copy(p[1:min(4, n)])
    n <= 4 && return maximum(load)
    gap = p[1] > 1.10 * p[2]
    Λ = max(p[1], p[4] + p[5]); τ = C_TARGET * Λ
    for j in 5:n
        E = [m for m in 1:4 if load[m] + p[j] <= τ + 1e-15]
        m = isempty(E) ? argmin(load) : (gap ? E[argmin(load[E])] : E[argmax(load[E])])
        load[m] += p[j]
    end
    return maximum(load)
end

function main()
    rng = MersenneTwister(20261011)
    razor = [0.6, 0.5, 0.5, 0.4, 0.4, 0.4, 0.3, 0.3, 0.3, 0.3]
    ρ = C_TARGET; bb = 1 / (2ρ); aa = 1 - bb
    rhofam = [aa, aa, aa, bb, bb, bb, 1/3, 1/3, 1/3]
    branchB = [0.59327, 0.5, 0.5, 0.44039, 0.40673, 0.40673, 0.31346, 0.2798, 0.2798, 0.2798]
    v1fail = [0.5, 0.5, 0.4, 0.4, 0.4, 0.4, 0.3, 0.3, 0.3]
    h1fail = [0.5, 0.5, 0.5, 0.4, 0.4, 0.4, 0.3, 0.3, 0.3]
    v4fail = [0.5, 0.5, 0.5, 0.5, 0.5, 0.4, 0.4, 0.3, 0.3]
    bases = [razor, rhofam, branchB, v1fail, h1fail, v4fail]
    worst = (-Inf, Float64[])
    N = 150_000
    for it in 1:N
        fam = rand(rng, 1:8)
        p = if fam <= 2
            n = rand(rng, 5:12); k = rand(rng, 2:4)
            vals = sort(rand(rng, 2:9, k) ./ 10; rev = true)
            q = Float64[]; while length(q) < n; push!(q, vals[rand(rng, 1:k)]); end
            sort(q; rev = true)
        elseif fam == 3
            n = rand(rng, 5:12); sort(0.25 .+ 0.75 .* rand(rng, n); rev = true)
        else
            sort([b0 * (1 + 0.08 * (rand(rng) - 0.5)) for b0 in bases[fam-3]]; rev = true)
        end
        cs = opt_makespan(p, 4)
        r = simHgap(p) / cs
        if r > worst[1]; worst = (r, p); end
    end
    r, p = worst
    @printf("H-gap 攻击最坏 = %.6f  n=%d  实例=%s\n", r, length(p), string(round.(p, digits=4)))
    @printf("对照：A4c 真值 6/5=1.2；候选目标 <1.19\n")
end
main()
