# 位次 4 倒置支（M4 收 p8，但 p7 的接收机 ∈ {M1,M2}）的数值定位：
# max(min+z)、最差实例形状、以及 τ 窗口 [p_k+p7, p_k+p6) 的实证宽度
include("/Users/a123456/math/半在线研究/SOSDP上界_algA_5over4/code/m3_a3_verify/jl/a4_lib.jl")
using Random, Printf

function main()
    rng = MersenneTwister(31); N = 400_000
    razor = [7/12, 7/12, 0.5, 0.5, 5/12, 5/12, 1/3, 1/3, 1/3]
    tot = 0; best = -Inf; bp = Float64[]; binfo = (0, 0, 0.0, 0.0, 0.0)
    for _ in 1:N
        fam = rand(rng, (:grid, :razor, :smooth))
        p = if fam == :grid
            k = rand(rng, 1:3); vals = sort(rand(rng, 3:10, k) ./ 10; rev = true)
            q = Float64[]; while length(q) < 9; push!(q, vals[rand(rng, 1:k)]); end
            sort(q; rev = true)
        elseif fam == :razor
            sort([b0 * (1 + 0.12 * (rand(rng) - 0.5)) for b0 in razor]; rev = true)
        else
            sort(0.25 .+ 0.75 .* rand(rng, 9); rev = true)
        end
        pn = p ./ opt_makespan(p, 4)
        pn[9] < 4/15 - 1e-12 && continue
        Λ = max(pn[1], pn[4] + pn[5]); τ = C_TARGET * Λ
        load = copy(pn[1:4]); cnt = ones(Int, 4); rec = zeros(Int, 9)
        okz = false; mR = 0
        for j in 5:9
            E = [m for m in 1:4 if load[m] + pn[j] <= τ + 1e-15]
            m = isempty(E) ? argmin(load) : E[argmax(load[E])]
            rec[j] = m
            if j == 9; okz = isempty(E); mR = m; end
            load[m] += pn[j]; cnt[m] += 1
        end
        okz || continue                        # z 兜底
        rec[8] == 4 || continue                # M4 收 p8（位次 4）
        rec[7] ∈ (1, 2) || continue            # 倒置：大件机收 p7
        sort(rec[5:7]) == [1, 2, 3] || continue
        cnt[mR] -= 1
        sort(cnt; rev = true) == [2, 2, 2, 2] || continue
        tot += 1
        z = pn[9]; pre = copy(load); pre[mR] -= z
        v = minimum(pre) + z
        if v > best
            k = rec[7]
            best = v; bp = pn
            binfo = (k, rec[5], pn[k] + pn[7], pn[k] + pn[6], τ)
        end
    end
    k, w1, lo, hi, τ = binfo
    @printf("位次4-倒置支 层(3)实例 %d 条；max(min+z) = %.6f（对照：干净级联 razor 7/6=1.16667，6/5=1.2）\n", tot, best)
    @printf("最差实例 p = %s\n", string(round.(bp, digits=5)))
    @printf("z = %.5f ；p7 接收机 M%d，W1=M%d；τ 窗口 [p%d+p7, p%d+p6) = [%.5f, %.5f)，τ=%.5f（宽 %.5f）\n",
            bp[9], k, w1, k, k, lo, hi, τ, hi - lo)
    @printf("校验：min+z−6/5 = %.6f（应 <0）\n", best - 1.2)
end
main()
