# a4_recv_cnt_check.jl —— 检验"引理 B"：z 兜底时接收机在放 z 前是否恒 ≤2 件
#   引理 B 是 agent-14 组合化约的承重墙（目前只有 n=10/Λ=p45 的 6533 片机器验证 + 采样）。
#   这里在全域采样（n=5..12，z ≥ 4/15 的兜底实例）统计接收机放 z 前的件数分布。
include("a4_lib.jl")
using Random, Printf

function main()
    rng = MersenneTwister(99)
    hist = Dict{Int, Int}()          # 接收机件数 -> 次数
    worst3 = (margin = Inf, pn = Float64[], cnt = 0)
    nfb = 0
    for n in 5:12
        for _ in 1:60000
            p = sort(Float64[rand(rng, 1:20) / 20 for _ in 1:n]; rev = true)
            cs = opt_makespan(p, 4); pn = p ./ cs
            pn[n] < 4 / 15 - 1e-12 && continue
            load = zeros(4); cnt = zeros(Int, 4)
            for j in 1:4; load[j] = pn[j]; cnt[j] = 1; end
            Λ = max(pn[1], pn[4] + pn[5]); τ = C_TARGET * Λ
            mR = 0; isfb = false
            for j in 5:n
                E = [m for m in 1:4 if load[m] + pn[j] <= τ + 1e-15]
                a = isempty(E) ? argmin(load) : E[argmax(load[E])]
                if j == n; isfb = isempty(E); mR = a; end
                load[a] += pn[j]; cnt[a] += 1
            end
            isfb || continue
            nfb += 1
            cR = cnt[mR] - 1                   # 放 z 前接收机件数
            hist[cR] = get(hist, cR, 0) + 1
            if cR >= 3
                z = pn[n]
                pre = copy(load); pre[mR] -= z
                margin = (1.2 - z) - minimum(pre)
                if margin < worst3.margin
                    worst3 = (margin, copy(pn), cR)
                end
            end
        end
    end
    println("兜底实例总数 = ", nfb)
    println("接收机放 z 前件数分布 = ", sort!(collect(hist)))
    if worst3.margin < Inf
        @printf("接收机 ≥3 件的实例中，引理 M 最差余量 = %.5f（件数 %d）\n", worst3.margin, worst3.cnt)
        println("  实例 = ", round.(worst3.pn, digits = 4))
    else
        println("接收机 ≥3 件的实例：0 条")
    end
end

main()
