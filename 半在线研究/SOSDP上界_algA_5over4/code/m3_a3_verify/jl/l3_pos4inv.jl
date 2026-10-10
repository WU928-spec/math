# 位次4 倒置支（FFFF、M4 收 p8、收 p7 的是 M1 或 M2）聚焦采样：测余量量级
include("/Users/a123456/math/半在线研究/SOSDP上界_algA_5over4/code/m3_a3_verify/jl/a4_lib.jl")
using Random, Printf

function main(N)
    rng = MersenneTwister(20261010)
    tot = 0; inv_tot = 0; viol = 0
    worst = -Inf; worst_p = Float64[]
    worst_slack = Inf; min_gap = Inf
    n_min_not_m4 = 0
    for _ in 1:N
        n = 9
        fam = rand(rng, (:grid, :blocks, :pow, :two))
        p = if fam == :grid
            k = rand(rng, 2:4); vals = sort(rand(rng, k) ./ 1; rev = true)
            q = Float64[]; while length(q) < n; push!(q, vals[rand(rng, 1:k)]); end
            sort(q; rev = true)
        else
            gen_instance(n, rng; family = fam)
        end
        cs = opt_makespan(p, 4); pn = p ./ cs
        pn[end] < 4 / 15 - 1e-12 && continue
        load = copy(pn[1:4]); cnt = ones(Int, 4)
        Λ = max(pn[1], pn[4] + pn[5]); τ = C_TARGET * Λ
        recv = zeros(Int, 4)   # recv[j-4] = 收 p_j 的机器, j=5..8
        fills = true; ok = false; mR = 0
        for j in 5:n
            E = [m for m in 1:4 if load[m] + pn[j] <= τ + 1e-15]
            if j < n && isempty(E); fills = false; end
            m = isempty(E) ? argmin(load) : E[argmax(load[E])]
            if j <= n - 1; recv[j - 4] = m; else ok = isempty(E); mR = m; end
            load[m] += pn[j]; cnt[m] += 1
        end
        (ok && fills) || continue            # z 兜底 + FFFF
        recv[4] == 4 || continue             # M4 收 p8（位次 4）
        cnt[mR] -= 1
        sort(cnt; rev = true) == [2, 2, 2, 2] || continue
        tot += 1
        recv[3] in (1, 2) || continue        # 倒置支：收 p7 的是大件机
        inv_tot += 1
        z = pn[n]; pre = copy(load); pre[mR] -= z
        mn = minimum(pre)
        argmin(pre) != 4 && (n_min_not_m4 += 1)
        margin = (6 / 5 - z) - mn
        if mn - (6 / 5 - z) > worst; worst = mn - (6 / 5 - z); worst_p = copy(pn); end
        if mn > 6 / 5 - z
            viol += 1
        end
        # 轨迹窗结构量：slack = τ − (p_W3 + p7) ≥ 0；gap = p6 − p7
        w3 = recv[3]
        slack = τ - (pre[w3] - pn[7] + pn[7])  # = τ − ℓ_W3(pre)
        # 更直接：步 7 前的负载
        pre7 = pre[w3]                         # W3 终载 = p_{w3} + p7
        slack7 = τ - pre7
        gap = pn[6] - pn[7]
        slack7 < worst_slack && (worst_slack = slack7)
        gap < min_gap && (min_gap = gap)
        if margin < 0.02
            @printf("近紧: margin=%.5f z=%.4f τ=%.4f p1=%.4f p4=%.4f p6=%.4f p7=%.4f p8=%.4f min=%.5f W3=M%d slack7=%.5f gap=%.5f\n",
                margin, z, τ, pn[1], pn[4], pn[6], pn[7], pn[8], mn, w3, slack7, gap)
        end
    end
    @printf("层(3) FFFF+M4末位 总 %d 条；倒置支 %d 条（占比 %.4f）；违例 %d 条\n", tot, inv_tot, inv_tot / max(tot, 1), viol)
    @printf("min≠ℓ_M4 的条数 %d；步7 slack 最小值 %.5f；p6−p7 最小间隔 %.5f\n", n_min_not_m4, worst_slack, min_gap)
    if viol > 0
        @printf("最差超出 %.5f 于 %s\n", worst, string(worst_p))
    else
        @printf("最接近边界: min+z−6/5 = %.5f（安全侧），实例 %s\n", worst, string(round.(worst_p; digits = 5)))
    end
end
main(150000)
