# l3_patterns.jl —— 层 (3)（n=9, 计数 {2,2,2,2}）兜底实例的步 5..8 填/兜模式分布 + 余量
include("/Users/a123456/math/半在线研究/SOSDP上界_algA_5over4/code/m3_a3_verify/jl/a4_lib.jl")
using Random, Printf

function main(N)
    rng = MersenneTwister(20261010)
    patcnt = Dict{String,Int}(); patworst = Dict{String,Float64}()
    pworst_all = Inf; p_inst = Float64[]
    for _ in 1:N
        n = 9
        fam = rand(rng, (:grid, :tight2, :two, :blocks))
        p = if fam == :grid
            k = rand(rng, 1:3); vals = sort(rand(rng, 3:10, k) ./ 10; rev = true)
            q = Float64[]; while length(q) < n; push!(q, vals[rand(rng, 1:k)]); end
            sort(q; rev = true)
        elseif fam == :tight2
            base = [7 / 12, 7 / 12, 0.5, 0.5, 5 / 12, 5 / 12, 1 / 3, 1 / 3, 1 / 3]
            sort([b * (1 + 0.1 * (rand(rng) - 0.5)) for b in base]; rev = true)
        elseif fam == :two
            a = 4 / 15 + rand(rng) * 0.6; b = 4 / 15 + rand(rng) * (a - 4 / 15)
            k = rand(rng, 1:n); sort(vcat(fill(a, k), fill(b, n - k)); rev = true)
        else
            gen_instance(n, rng; family = :blocks, lower = 4 / 15 + 1e-9)
        end
        cs = opt_makespan(p, 4); pn = p ./ cs
        pn[end] < 4 / 15 - 1e-12 && continue
        # 模拟并记录
        load = copy(pn[1:4]); cnt = ones(Int, 4); Λ = max(pn[1], pn[4] + pn[5]); τ = C_TARGET * Λ
        pat = Bool[]; mR = 0; ok = true
        for j in 5:n
            E = [m for m in 1:4 if load[m] + pn[j] <= τ + 1e-15]
            if isempty(E)
                m = argmin(load); push!(pat, true)
            else
                m = E[argmax(load[E])]; push!(pat, false)
            end
            j == n && (mR = m; isempty(E) || (ok = false))
            load[m] += pn[j]; cnt[m] += 1
        end
        ok || continue                       # z 必须兜底
        cnt[mR] -= 1
        sort(cnt; rev = true) != [2, 2, 2, 2] && continue   # 只要层 (3)
        z = pn[n]; pre = copy(load); pre[mR] -= z
        margin = (7 / 6 - z) - minimum(pre)    # 层 (3) 目标 7/6 的余量（>0 好）
        key = join(map(b -> b ? "B" : "F", pat), "")
        patcnt[key] = get(patcnt, key, 0) + 1
        margin < get(patworst, key, Inf) && (patworst[key] = margin)
        if margin < pworst_all; pworst_all = margin; p_inst = copy(pn); end
    end
    println("层 (3) 模式分布（步5..8, F=fill B=fallback）：")
    for k in sort(collect(keys(patcnt)))
        @printf("  %s : %6d 条   最差7/6余量 %.5f\n", k, patcnt[k], patworst[k])
    end
    @printf("全层最差余量 %.5f  实例 %s\n", pworst_all, join(round.(p_inst, digits=4), " "))
end
main(length(ARGS) >= 1 ? parse(Int, ARGS[1]) : 40000)
