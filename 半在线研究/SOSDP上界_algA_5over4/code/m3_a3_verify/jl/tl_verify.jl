# tl_verify.jl — TL 与 min-版的数值复核 + 按接收机结构分层
#   TL: z 兜底 ⟹ 放 z 前 三轻之和 ≤ 3.6 − 3z
#   min-版(充分): z 兜底 ⟹ min ≤ 6/5 − z
#   分层: 接收机 (f,b) = (填充数, 兜底数); 计数向量; Λ 分支
include("/Users/a123456/math/半在线研究/SOSDP上界_algA_5over4/code/m3_a3_verify/jl/a4_lib.jl")
using Random, Printf

const RHO = C_TARGET

"带逐步记录的 A4c 模拟（与 a4_sim 的 [:p1,:p45]、无 slot、无 branch 一致）"
function sim_trace(pn)
    n = length(pn); load = zeros(4)
    Λ = max(pn[1], pn[4] + pn[5]); τ = RHO * Λ
    hist = Tuple{Int,Bool}[]        # (machine, is_fallback)
    for j in 1:min(4, n); load[j] += pn[j]; end
    for j in 5:n
        E = [m for m in 1:4 if load[m] + pn[j] <= τ + 1e-15]
        if isempty(E)
            m = argmin(load); push!(hist, (m, true))
        else
            m = E[argmax(load[E])]; push!(hist, (m, false))
        end
        load[m] += pn[j]
    end
    return load, hist, τ, Λ
end

function one!(pn, stats)
    n = length(pn); z = pn[n]
    load, hist, τ, Λ = sim_trace(pn)
    isempty(hist) && return
    (mR, isfb) = hist[end]
    isfb || return
    stats.nfb[] += 1
    pre = copy(load); pre[mR] -= z
    L = sort(pre)
    m3 = (3.6 - 3z) - (L[1] + L[2] + L[3])       # TL 余量
    m1 = (1.2 - z) - L[1]                        # min-版余量
    m3 < -1e-9 && (stats.v3[] += 1)
    m1 < -1e-9 && (stats.v1[] += 1)
    # 接收机结构
    f = count(h -> h[1] == mR && !h[2], hist)
    b = count(h -> h[1] == mR && h[2], hist)
    cnt = zeros(Int, 4)
    for (mm, _) in hist; cnt[mm] += 1; end
    cnt .+= 1
    key = (f, b, sort(cnt, rev = true), Λ == pn[1] ? :p1 : :p45, n)
    c = get(stats.casecnt, key, 0) + 1; stats.casecnt[key] = c
    if m1 < get(stats.worst, key, Inf)
        stats.worst[key] = m1
        stats.worstp[key] = copy(pn)
    end
    m1 < stats.w1[] && (stats.w1[] = m1; stats.p1[] = copy(pn))
    m3 < stats.w3[] && (stats.w3[] = m3; stats.p3[] = copy(pn))
    return
end

function gen(rng, n, fam)
    if fam == :grid      # 块常值：1-3 个不同值 {0.3..1.0/0.1}
        k = rand(rng, 1:3); vals = sort(rand(rng, 3:10, k) ./ 10; rev = true)
        p = Float64[]
        while length(p) < n; push!(p, vals[rand(rng, 1:k)]); end
        return sort(p[1:n]; rev = true)
    elseif fam == :tight2  # 绕临界实例 (0.6,0.5,0.5,0.4,0.4,0.4,0.3,0.3,0.3,0.3) 扰动
        base = [0.6, 0.5, 0.5, 0.4, 0.4, 0.4, 0.3, 0.3, 0.3, 0.3]
        p = [base[mod1(i, 10)] * (1 + 0.12 * (rand(rng) - 0.5)) for i in 1:n]
        return sort(p; rev = true)
    else
        return gen_instance(n, rng; family = fam, lower = 4 / 15 + 1e-9)
    end
end

function main(N)
    stats = (nfb = Ref(0), v3 = Ref(0), v1 = Ref(0),
             casecnt = Dict{Any,Int}(), worst = Dict{Any,Float64}(), worstp = Dict{Any,Vector{Float64}}(),
             w1 = Ref(Inf), p1 = Ref(Float64[]), w3 = Ref(Inf), p3 = Ref(Float64[]))
    rng = MersenneTwister(20261008)
    fams = (:pow, :blocks, :two, :general, :grid, :tight2)
    t0 = time()
    for n in 5:12, rep in 1:N
        fam = fams[rand(rng, 1:length(fams))]
        p = gen(rng, n, fam)
        cs = opt_makespan(p, 4)
        cs <= 0 && continue
        pn = p ./ cs
        pn[end] < 4 / 15 - 1e-12 && continue
        one!(pn, stats)
    end
    println("=== 用时 $(round(time()-t0, digits=1))s, 兜底实例 $(stats.nfb[]) ===")
    println("TL 违反: $(stats.v3[])   min-版违反: $(stats.v1[])")
    @printf("最差 TL 余量 %.6f  实例 %s\n", stats.w3[], join(round.(stats.p3[], digits=4), " "))
    @printf("最差 min 余量 %.6f  实例 %s\n", stats.w1[], join(round.(stats.p1[], digits=4), " "))
    println("--- 分层 (f,b,计数,Λ,n): 条数 / 最差 min 余量 ---")
    for k in sort(collect(keys(stats.casecnt)))
        @printf("%s : %d / %.5f\n", string(k), stats.casecnt[k], stats.worst[k])
    end
end
main(length(ARGS) >= 1 ? parse(Int, ARGS[1]) : 4000)
