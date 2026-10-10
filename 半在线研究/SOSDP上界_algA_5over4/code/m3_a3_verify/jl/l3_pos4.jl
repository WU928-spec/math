# 位次4（FFFF、M4=W4）干净级联验证：在 H（全负载 > 6/5−z）下沿轨迹检查 p3+p4 与 ℓ4
include("/Users/a123456/math/半在线研究/SOSDP上界_algA_5over4/code/m3_a3_verify/jl/a4_lib.jl")
using Random, Printf
function main(N)
    rng = MersenneTwister(99); tot = 0; nH = 0; worst = -Inf
    for _ in 1:N
        n = 9
        fam = rand(rng, (:grid, :tight2, :blocks))
        p = if fam == :grid
            k = rand(rng, 1:3); vals = sort(rand(rng, 3:10, k) ./ 10; rev = true)
            q = Float64[]; while length(q) < n; push!(q, vals[rand(rng, 1:k)]); end
            sort(q; rev = true)
        elseif fam == :tight2
            base = [7 / 12, 7 / 12, 0.5, 0.5, 5 / 12, 5 / 12, 1 / 3, 1 / 3, 1 / 3]
            sort([b0 * (1 + 0.12 * (rand(rng) - 0.5)) for b0 in base]; rev = true)
        else
            gen_instance(n, rng; family = :blocks, lower = 4 / 15 + 1e-9)
        end
        cs = opt_makespan(p, 4); pn = p ./ cs
        pn[end] < 4 / 15 - 1e-12 && continue
        load = copy(pn[1:4]); cnt = ones(Int, 4)
        Λ = max(pn[1], pn[4] + pn[5]); τ = C_TARGET * Λ
        ok = false; mR = 0; fills = true; recv8 = 0
        for j in 5:n
            E = [m for m in 1:4 if load[m] + pn[j] <= τ + 1e-15]
            if j < n && isempty(E); fills = false; end   # 步5..8 有兜底则非 FFFF
            m = isempty(E) ? argmin(load) : E[argmax(load[E])]
            j == n && (ok = isempty(E); mR = m); j == n - 1 && (recv8 = m)
            load[m] += pn[j]; cnt[m] += 1
        end
        (ok && fills) || continue
        cnt[mR] -= 1
        sort(cnt; rev = true) == [2, 2, 2, 2] || continue
        recv8 == 4 || continue                  # M4 收 p8（位次 4）
        tot += 1
        z = pn[n]; pre = copy(load); pre[mR] -= z
        # 干净级联检查：W_i = M_i
        sort(cnt) == [2, 2, 2, 2] || continue
        mn = minimum(pre)
        if mn > 6 / 5 - z                      # H 下的实际实例（预期没有）
            nH += 1; worst = max(worst, mn - (6 / 5 - z))
        end
    end
    @printf("FFFF+M4末位的层(3)实例 %d 条；其中 H（min>6/5−z）的 %d 条（应为 0）；最差超出 %.5f\n", tot, nH, worst)
end
main(80000)
