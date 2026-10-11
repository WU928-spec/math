# H5i：ρ 线 fullest-eligible；但若步 5 的填充没进 M1（M1 对 p5 不合格）⟹ 步 6 起切最轻合格
include("/Users/a123456/math/半在线研究/SOSDP上界_algA_5over4/code/m3_a3_verify/jl/a4_lib.jl")
using Random, Printf
function simH5i(p)
    n = length(p); load = copy(p[1:min(4, n)])
    n <= 4 && return maximum(load)
    Λ = max(p[1], p[4] + p[5]); τ = C_TARGET * Λ
    lpt = false
    for j in 5:n
        E = [m for m in 1:4 if load[m] + p[j] <= τ + 1e-15]
        m = isempty(E) ? argmin(load) : (lpt ? E[argmin(load[E])] : E[argmax(load[E])])
        j == 5 && m != 1 && (lpt = true)   # 步 5 没进 M1 ⟹ 切换
        load[m] += p[j]
    end
    return maximum(load)
end
ρ = C_TARGET; bb = 1 / (2ρ); aa = 1 - bb
tests = [
    ("razor",       [0.6, 0.5, 0.5, 0.4, 0.4, 0.4, 0.3, 0.3, 0.3, 0.3]),
    ("n9兄弟",       [0.6, 0.5, 0.5, 0.4, 0.4, 0.3, 0.3, 0.3, 0.3]),
    ("三平头H1死",   [0.5, 0.5, 0.5, 0.4, 0.4, 0.4, 0.3, 0.3, 0.3]),
    ("V1死",        [0.5, 0.5, 0.4, 0.4, 0.4, 0.4, 0.3, 0.3, 0.3]),
    ("V4死",        [0.5, 0.5, 0.5, 0.5, 0.5, 0.4, 0.4, 0.3, 0.3]),
    ("ρ族端点",      [aa, aa, aa, bb, bb, bb, 1/3, 1/3, 1/3]),
    ("分支B最差",    [0.59327, 0.5, 0.5, 0.44039, 0.40673, 0.40673, 0.31346, 0.2798, 0.2798, 0.2798]),
    ("姐妹前缀",     [0.6, 0.5, 0.5, 0.4, 0.4]),
]
println("—— H5i 点检 ——")
for (nm, p) in tests
    r = simH5i(p) / opt_makespan(p, 4)
    println(rpad(nm, 14), " 比值=", round(r, digits=6), r > 1.19 + 1e-9 ? "  ⚠️" : "  ✓")
end
# 正式筛查
function screen()
    rng = MersenneTwister(20261011)
    bases = [t[2] for t in tests[1:6]]
    worst = (-Inf, Float64[]); N = 150_000
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
        r = simH5i(p) / opt_makespan(p, 4)
        r > worst[1] && (worst = (r, p))
    end
    @printf("H5i 攻击最坏 = %.6f  n=%d  实例=%s\n", worst[1], length(worst[2]), string(round.(worst[2], digits=4)))
end
screen()
