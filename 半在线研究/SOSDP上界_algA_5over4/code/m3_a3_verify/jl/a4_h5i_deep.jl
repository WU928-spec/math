# H5i 加深筛查：3 种子 × 150k + 最差实例细噪声扰动 + 平滑下降族
# 目的：检验"采样最坏钉在 ρ"是否稳固，还是更深攻击能把它推向 6/5
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
        j == 5 && m != 1 && (lpt = true)
        load[m] += p[j]
    end
    return maximum(load)
end

function main()
    ρ = C_TARGET; bb = 1 / (2ρ); aa = 1 - bb
    worst_inst = [0.8493, 0.7694, 0.76, 0.7472, 0.7222, 0.6806, 0.5668, 0.2845]
    razor = [0.6, 0.5, 0.5, 0.4, 0.4, 0.4, 0.3, 0.3, 0.3, 0.3]
    rhofam = [aa, aa, aa, bb, bb, bb, 1/3, 1/3, 1/3]
    branchB = [0.59327, 0.5, 0.5, 0.44039, 0.40673, 0.40673, 0.31346, 0.2798, 0.2798, 0.2798]
    worst = (-Inf, Float64[], 0, 0)
    for seed in (11, 22, 33)
        rng = MersenneTwister(seed)
        for it in 1:150_000
            fam = rand(rng, 1:9)
            p = if fam <= 2
                n = rand(rng, 5:12); k = rand(rng, 2:4)
                vals = sort(rand(rng, 2:9, k) ./ 10; rev = true)
                q = Float64[]; while length(q) < n; push!(q, vals[rand(rng, 1:k)]); end
                sort(q; rev = true)
            elseif fam == 3
                n = rand(rng, 5:12); sort(0.25 .+ 0.75 .* rand(rng, n); rev = true)
            elseif fam == 4          # 平滑下降族（worst 实例的家乡）
                n = rand(rng, 5:10); sort(rand(rng, n); rev = true)
            elseif fam <= 7          # razor/ρ族/分支B 扰动
                base = (razor, rhofam, branchB)[fam - 4]
                sort([b0 * (1 + 0.06 * (rand(rng) - 0.5)) for b0 in base]; rev = true)
            else                     # worst 实例细噪声
                sort([b0 * (1 + 0.03 * (rand(rng) - 0.5)) for b0 in worst_inst]; rev = true)
            end
            r = simH5i(p) / opt_makespan(p, 4)
            r > worst[1] && (worst = (r, p, seed, fam))
        end
        @printf("seed=%d 完成\n", seed); flush(stdout)
    end
    r, p, seed, fam = worst
    @printf("H5i 加深攻击最坏 = %.6f  n=%d seed=%d fam=%d\n实例=%s\n", r, length(p), seed, fam, string(round.(p, digits=4)))
    @printf("对照：ρ=%.6f、6/5=1.2； razor=1.2（A4c 紧）\n", ρ)
end
main()
