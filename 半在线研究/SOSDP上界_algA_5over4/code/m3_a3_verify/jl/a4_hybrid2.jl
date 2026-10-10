# H11/H12：首件安全配对（A3 架构的 m=4 提升版）
include("/Users/a123456/math/半在线研究/SOSDP上界_algA_5over4/code/m3_a3_verify/jl/a4_lib.jl")
using Random, Printf

function simH2(p, kind::Symbol)
    n = length(p); load = copy(p[1:min(4, n)]); cnt = ones(Int, min(4, n))
    n <= 4 && return maximum(load)
    Λ = max(p[1], p[4] + p[5]); τ = C_TARGET * Λ
    for j in 5:n
        # 安全配对强制：M1 只含 p1 且 p1+p_j ≤ 1（≤C* 本质安全）→ 入 M1
        if cnt[1] == 1 && load[1] + p[j] <= 1 + 1e-15
            if kind ∈ (:H11, :H12) && (j == 5 || kind == :H12)
                load[1] += p[j]; cnt[1] += 1; continue
            end
        end
        E = [m for m in 1:4 if load[m] + p[j] <= τ + 1e-15]
        m = isempty(E) ? argmin(load) : E[argmax(load[E])]
        load[m] += p[j]; cnt[m] += 1
    end
    return maximum(load)
end

function main()
    rng = MersenneTwister(777)
    razor = [0.6, 0.5, 0.5, 0.4, 0.4, 0.4, 0.3, 0.3, 0.3, 0.3]
    ρ = C_TARGET; bb = 1 / (2ρ); aa = 1 - bb
    rhofam = [aa, aa, aa, bb, bb, bb, 1/3, 1/3, 1/3]
    branchB = [0.59327, 0.5, 0.5, 0.44039, 0.40673, 0.40673, 0.31346, 0.2798, 0.2798, 0.2798]
    v1fail = [0.5, 0.5, 0.4, 0.4, 0.4, 0.4, 0.3, 0.3, 0.3]
    h1fail = [0.5, 0.5, 0.5, 0.4, 0.4, 0.4, 0.3, 0.3, 0.3]
    v4fail = [0.5, 0.5, 0.5, 0.5, 0.5, 0.4, 0.4, 0.3, 0.3]
    Ks = [:H11, :H12]
    worst = Dict(k => (-Inf, Float64[]) for k in Ks)
    N = 200_000
    for it in 1:N
        fam = rand(rng, 1:9)
        base = fam == 4 ? razor : fam == 5 ? rhofam : fam == 6 ? branchB : fam == 7 ? v1fail : fam == 8 ? h1fail : v4fail
        p = if fam <= 2
            n = rand(rng, 5:12); k = rand(rng, 2:4)
            vals = sort(rand(rng, 2:9, k) ./ 10; rev = true)
            q = Float64[]; while length(q) < n; push!(q, vals[rand(rng, 1:k)]); end
            sort(q; rev = true)
        elseif fam == 3
            n = rand(rng, 5:12); sort(0.25 .+ 0.75 .* rand(rng, n); rev = true)
        else
            sort([b0 * (1 + 0.08 * (rand(rng) - 0.5)) for b0 in base]; rev = true)
        end
        cs = opt_makespan(p, 4)
        for k in Ks
            r = simH2(p, k) / cs
            if r > worst[k][1]; worst[k] = (r, p); end
        end
    end
    println("A3 架构提升版筛查（", N, " 实例，含全部历史死亡点的扰动）")
    for k in Ks
        r, p = worst[k]
        @printf("%s  攻击最坏=%.6f  n=%2d  实例=%s\n", k, r, length(p), string(round.(p, digits=4)))
    end
    # 死亡点逐一核验
    for (nm, inst) in [("razor", razor), ("(0.5³,0.4³,0.3³)", h1fail), ("V1死", v1fail), ("V4死", v4fail), ("ρ族", rhofam)]
        cs = opt_makespan(inst, 4)
        @printf("核验 %-16s C*=%.4f  H11=%.4f  H12=%.4f\n", nm, cs, simH2(inst, :H11)/cs, simH2(inst, :H12)/cs)
    end
end
main()
