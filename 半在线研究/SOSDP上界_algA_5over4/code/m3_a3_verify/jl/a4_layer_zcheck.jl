# a4_layer_zcheck.jl —— 检验层 (1)(2) 的"补杀方向"：近失败实例的 z 分布
#   若体积法封闭的是 z ≤ 3/10（我的代数结论），则近失败（min_pre 接近 6/5−z）应集中在 z > 3/10；
#   若 agent-14 文档标注（z < 3/10 开放）正确，则近失败应集中在 z < 3/10。
include("a4_lib.jl")
using Random, Printf

function main()
    rng = MersenneTwister(2026)
    # 键： (n, 计数多重集) ；值：(最差余量, 对应 z, 实例)
    worst = Dict{Any, Tuple{Float64, Float64, Vector{Float64}}}()
    cnts = Dict{Any, Int}()
    for n in (8, 9, 10, 11)
        for _ in 1:60000
            p = sort(Float64[rand(rng, 1:20) / 20 for _ in 1:n]; rev = true)
            cs = opt_makespan(p, 4); pn = p ./ cs
            pn[n] < 4 / 15 - 1e-12 && continue
            load = zeros(4); cnt = ones(Int, 4)
            for j in 1:4; load[j] = pn[j]; end
            Λ = max(pn[1], pn[4] + pn[5]); τ = C_TARGET * Λ
            mR = 0; isfb = false
            for j in 5:n
                E = [m for m in 1:4 if load[m] + pn[j] <= τ + 1e-15]
                a = isempty(E) ? argmin(load) : E[argmax(load[E])]
                if j == n; isfb = isempty(E); mR = a; end
                load[a] += pn[j]; cnt[a] += 1
            end
            isfb || continue
            z = pn[n]
            pre = copy(load); pre[mR] -= z
            cnt[mR] -= 1                       # 放 z 前的计数
            key = (n, sort(cnt, rev = true))
            cnts[key] = get(cnts, key, 0) + 1
            margin = (1.2 - z) - minimum(pre)   # 引理 M 余量（>0 好；越小越接近失败）
            if margin < get(worst, key, (Inf, 0.0, Float64[]))[1]
                worst[key] = (margin, z, copy(pn))
            end
        end
    end
    println("各 (n, 放z前计数) 的最差余量与对应 z：")
    for k in sort!(collect(keys(worst)); by = k -> (k[1], -k[2]))
        (m, z, _) = worst[k]
        @printf("n=%2d counts=%s  样本 %6d  最差余量 %8.5f  @ z=%.4f\n", k[1], k[2], cnts[k], m, z)
    end
end

main()
