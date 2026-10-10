include("/Users/a123456/math/半在线研究/SOSDP上界_algA_5over4/code/m3_a3_verify/jl/a4_lib.jl")
using Random, Printf
rng = MersenneTwister(777)
worst = Tuple{Float64,Float64,Vector{Float64},String}[]
for _ in 1:120000
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
    ok = false; mR = 0; pat = Bool[]
    for j in 5:n
        E = [m for m in 1:4 if load[m] + pn[j] <= τ + 1e-15]
        m = isempty(E) ? argmin(load) : E[argmax(load[E])]
        push!(pat, isempty(E))
        j == n && (mR = m; ok = isempty(E))
        load[m] += pn[j]; cnt[m] += 1
    end
    ok || continue
    cnt[mR] -= 1
    sort(cnt; rev = true) == [2, 2, 2, 2] || continue
    z = pn[n]; pre = copy(load); pre[mR] -= z
    margin = (7 / 6 - z) - minimum(pre)
    push!(worst, (margin, z, pn, join(map(b -> b ? "B" : "F", pat), "")))
end
sort!(worst; by = t -> t[1])
println("层(3) 最差 10 条（7/6 余量, z, 模式, 实例前4件）:")
for t in worst[1:min(10, length(worst))]
    @printf("  余量 %.5f  z=%.4f  模式 %s  p=%s\n", t[1], t[2], t[4], join(round.(t[3][1:4], digits=3), " "))
end
@printf("余量<0.01 的实例中 z=1/3±0.005 占比: ")
lo = [t for t in worst if t[1] < 0.01]
println(count(t -> abs(t[2] - 1 / 3) < 0.005, lo), "/", length(lo))
