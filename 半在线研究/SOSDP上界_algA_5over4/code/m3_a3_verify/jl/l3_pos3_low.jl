# 位次3（M4 收 p7）的 z≤3/10 段聚焦采样：余量量级 + 结构（共箱对、匹配、min 身份）
include("/Users/a123456/math/半在线研究/SOSDP上界_algA_5over4/code/m3_a3_verify/jl/a4_lib.jl")
using Random, Printf

function main(N)
    rng = MersenneTwister(777)
    tot = 0; seg = 0; viol = 0
    worst = -Inf; worst_p = Float64[]
    minid = Dict{Int,Int}()
    for _ in 1:N
        n = 9
        fam = rand(rng, (:grid, :blocks, :pow, :two))
        p = if fam == :grid
            k = rand(rng, 2:4); vals = sort(rand(rng, k); rev = true)
            q = Float64[]; while length(q) < n; push!(q, vals[rand(rng, 1:k)]); end
            sort(q; rev = true)
        else
            gen_instance(n, rng; family = fam)
        end
        cs = opt_makespan(p, 4); pn = p ./ cs
        pn[end] < 4 / 15 - 1e-12 && continue
        load = copy(pn[1:4]); cnt = ones(Int, 4)
        Λ = max(pn[1], pn[4] + pn[5]); τ = C_TARGET * Λ
        recv = zeros(Int, 4); ok = false; mR = 0
        for j in 5:n
            E = [m for m in 1:4 if load[m] + pn[j] <= τ + 1e-15]
            m = isempty(E) ? argmin(load) : E[argmax(load[E])]
            if j <= n - 1; recv[j - 4] = m; else ok = isempty(E); mR = m; end
            load[m] += pn[j]; cnt[m] += 1
        end
        ok || continue                          # z 兜底
        cnt[mR] -= 1
        sort(cnt; rev = true) == [2, 2, 2, 2] || continue
        recv[3] == 4 || continue                # M4 收 p7（位次 3）
        tot += 1
        z = pn[n]
        z <= 0.3 + 1e-12 || continue            # 低 z 段
        seg += 1
        pre = copy(load); pre[mR] -= z
        mn = minimum(pre); am = argmin(pre)
        minid[am] = get(minid, am, 0) + 1
        margin = (6 / 5 - z) - mn
        if mn - (6 / 5 - z) > worst
            worst = mn - (6 / 5 - z); worst_p = copy(pn)
            @printf("新最差: min+z-6/5=%.5f z=%.4f τ=%.4f recv=%s p=%s min机=M%d\n",
                worst, z, τ, string(recv), string(round.(pn; digits = 4)), am)
        end
        mn > 6 / 5 - z && (viol += 1)
    end
    @printf("位次3 总 %d 条；z≤3/10 段 %d 条；违例 %d；最差 min+z-6/5 = %.5f\n", tot, seg, viol, worst)
    @printf("min 机分布: %s\n", string(minid))
    if !isempty(worst_p)
        @printf("最差实例: %s\n", string(round.(worst_p; digits = 5)))
    end
end
main(150000)
