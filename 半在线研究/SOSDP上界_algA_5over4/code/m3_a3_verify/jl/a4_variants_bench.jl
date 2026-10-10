# 变体全局天花板对比：改规则的代价在别处变高多少？
# 变体：V0=A4c（fullest, ρΛ）；V1=最轻合格（lightest, ρΛ）；V2=AlgA（fullest, 5/4·(p4+p5)）；V3=A4c+M1槽（slot, ρΛ）
# 采样：块常值格点 + razor/ρ族/分支B 最差实例的扰动 + 平滑随机；n=5..12
include("/Users/a123456/math/半在线研究/SOSDP上界_algA_5over4/code/m3_a3_verify/jl/a4_lib.jl")
using Random, Printf

# slot = A3 式 M1 单槽：M1 只含 p1 且合格 → 入 M1
function simV2(p, rule::Symbol, line::Symbol, slot::Bool)
    n = length(p); load = copy(p[1:min(4, n)]); cnt = ones(Int, min(4, n))
    n <= 4 && return maximum(load)
    Λ = line == :rho ? C_TARGET * max(p[1], p[4] + p[5]) : 1.25 * (p[4] + p[5])
    for j in 5:n
        E = [m for m in 1:4 if load[m] + p[j] <= Λ + 1e-15]
        m = if !isempty(E)
            if slot && cnt[1] == 1 && load[1] + p[j] <= Λ + 1e-15
                1
            elseif rule == :fullest
                E[argmax(load[E])]
            else
                E[argmin(load[E])]
            end
        else
            argmin(load)
        end
        load[m] += p[j]; cnt[m] += 1
    end
    return maximum(load)
end

function main()
    rng = MersenneTwister(20261010)
    razor = [0.6, 0.5, 0.5, 0.4, 0.4, 0.4, 0.3, 0.3, 0.3, 0.3]
    ρ = C_TARGET; bb = 1 / (2ρ); aa = 1 - bb
    rhofam = [aa, aa, aa, bb, bb, bb, 1/3, 1/3, 1/3]
    branchB = [0.59327, 0.5, 0.5, 0.44039, 0.40673, 0.40673, 0.31346, 0.2798, 0.2798, 0.2798]
    Vs = [("V0=A4c      ", :fullest, :rho, false), ("V1=最轻合格 ", :lightest, :rho, false),
          ("V2=AlgA-5/4 ", :fullest, :a54, false), ("V3=A4c+M1槽 ", :fullest, :rho, true)]
    worst = [(-Inf, Float64[]) for _ in Vs]
    N = 120_000
    for it in 1:N
        fam = rand(rng, 1:6)
        p = if fam <= 2                       # 块常值格点
            n = rand(rng, 5:12); k = rand(rng, 2:4)
            vals = sort(rand(rng, 2:9, k) ./ 10; rev = true)
            q = Float64[]; while length(q) < n; push!(q, vals[rand(rng, 1:k)]); end
            sort(q; rev = true)
        elseif fam == 3
            sort([b0 * (1 + 0.10 * (rand(rng) - 0.5)) for b0 in razor]; rev = true)
        elseif fam == 4
            sort([b0 * (1 + 0.10 * (rand(rng) - 0.5)) for b0 in rhofam]; rev = true)
        elseif fam == 5
            sort([b0 * (1 + 0.10 * (rand(rng) - 0.5)) for b0 in branchB]; rev = true)
        else
            n = rand(rng, 5:12); sort(0.25 .+ 0.75 .* rand(rng, n); rev = true)
        end
        cs = opt_makespan(p, 4)
        for (i, (_, rule, line, slot)) in enumerate(Vs)
            r = simV2(p, rule, line, slot) / cs
            if r > worst[i][1]; worst[i] = (r, p); end
        end
    end
    println("变体全局采样天花板（", N, " 实例；攻击最坏是真实最差的下界）")
    for (i, (nm, _, _, _)) in enumerate(Vs)
        r, p = worst[i]
        @printf("%s 攻击最坏=%.6f  n=%d  实例=%s\n", nm, r, length(p), string(round.(p, digits=4)))
    end
end
main()
