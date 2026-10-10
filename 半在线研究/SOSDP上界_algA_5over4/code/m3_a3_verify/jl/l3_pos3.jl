include("/Users/a123456/math/半在线研究/SOSDP上界_algA_5over4/code/m3_a3_verify/jl/a4_lib.jl")
using Random, Printf
function main(N)
    rng = MersenneTwister(4242)
    tot = 0; nH = 0; worst = -Inf; wi = Float64[]; wz = 0.0
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
        ok = false; mR = 0; recv7 = 0
        for j in 5:n
            E = [m for m in 1:4 if load[m] + pn[j] <= τ + 1e-15]
            m = isempty(E) ? argmin(load) : E[argmax(load[E])]
            j == n && (ok = isempty(E); mR = m); j == 7 && (recv7 = m)
            load[m] += pn[j]; cnt[m] += 1
        end
        ok || continue
        cnt[mR] -= 1
        sort(cnt; rev = true) == [2, 2, 2, 2] || continue
        recv7 == 4 || continue               # 位次 3：M4 收 p7
        tot += 1
        z = pn[n]; pre = copy(load); pre[mR] -= z
        lhs = minimum(pre) - (6 / 5 - z)
        if lhs > worst; worst = lhs; wi = copy(pn); wz = z; end
        lhs > -1e-9 && (nH += 1)
    end
    @printf("位次3 层(3)实例 %d 条；min>6/5−z 的 %d 条；最差(min+z)−6/5 = %.5f @ z = %.4f\n", tot, nH, worst, wz)
    println("最差实例: ", join(round.(wi, digits = 4), " "))
end
main(100000)
