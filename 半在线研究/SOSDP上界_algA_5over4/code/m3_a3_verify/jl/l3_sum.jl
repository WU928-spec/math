include("/Users/a123456/math/半在线研究/SOSDP上界_algA_5over4/code/m3_a3_verify/jl/a4_lib.jl")
using Random, Printf
function main(N)
    rng = MersenneTwister(31337)
    viol = 0; tot = 0; worst = -Inf; wi = Float64[]
    for _ in 1:N
        n = 9
        fam = rand(rng, (:grid, :tight2, :two, :blocks, :pow))
        p = if fam == :grid
            k = rand(rng, 1:3); vals = sort(rand(rng, 3:10, k) ./ 10; rev = true)
            q = Float64[]; while length(q) < n; push!(q, vals[rand(rng, 1:k)]); end
            sort(q; rev = true)
        elseif fam == :tight2
            base = [7 / 12, 7 / 12, 0.5, 0.5, 5 / 12, 5 / 12, 1 / 3, 1 / 3, 1 / 3]
            sort([b * (1 + 0.12 * (rand(rng) - 0.5)) for b in base]; rev = true)
        else
            gen_instance(n, rng; family = fam == :pow ? :pow : fam, lower = 4 / 15 + 1e-9)
        end
        cs = opt_makespan(p, 4); pn = p ./ cs
        pn[end] < 4 / 15 - 1e-12 && continue
        load = copy(pn[1:4]); cnt = ones(Int, 4)
        Λ = max(pn[1], pn[4] + pn[5]); τ = C_TARGET * Λ
        ok = false; mR = 0
        for j in 5:n
            E = [m for m in 1:4 if load[m] + pn[j] <= τ + 1e-15]
            m = isempty(E) ? argmin(load) : E[argmax(load[E])]
            j == n && (ok = isempty(E); mR = m)
            load[m] += pn[j]; cnt[m] += 1
        end
        ok || continue
        cnt[mR] -= 1
        sort(cnt; rev = true) == [2, 2, 2, 2] || continue
        tot += 1
        z = pn[n]
        pre = copy(load); pre[mR] -= z
        s34 = pre[3] + pre[4]
        lhs = s34 - (7 / 3 - 2z)
        lhs > 1e-9 && (viol += 1)
        if lhs > worst; worst = lhs; wi = copy(pn); end
    end
    @printf("层(3)兜底实例 %d 条；ℓ_M3+ℓ_M4 > 7/3−2z 的违例 %d 条；最大超出 %.5f\n", tot, viol, worst)
    println("最差实例: ", round.(wi, digits = 4))
end
main(120000)
