# a4_lemmaO_perturb.jl —— 在临界实例邻域内扰动采样，映射近失败区结构
#   中心：p* = (0.6,0.5,0.5,0.4,0.4,0.4,0.3,0.3,0.3,0.3)（C*=1，final=1.2 取等）
#   检验：近失败区里 引理O形式A/B 的余量、τ 界、机器件数分布、接收机件数
include("a4_lib.jl")
using Random, Printf

const PCRIT = [0.6, 0.5, 0.5, 0.4, 0.4, 0.4, 0.3, 0.3, 0.3, 0.3]

function probe(pn; rec)
    n = length(pn); z = pn[n]
    load = zeros(4); cnt = zeros(Int, 4)
    Λ = max(pn[1], pn[4] + pn[5]); τ = C_TARGET * Λ
    isfb = falses(n); q_r = NaN; recv_load = NaN; recv_cnt = 0; mR = 0
    for j in 1:4; load[j] += pn[j]; cnt[j] = 1; end
    for j in 5:n
        E = [m for m in 1:4 if load[m] + pn[j] <= τ + 1e-15]
        fb = isempty(E); isfb[j] = fb
        a = fb ? argmin(load) : E[argmax(load[E])]
        if j == n - 1 && fb
            q_r = minimum(load); recv_load = q_r + pn[j]; recv_cnt = cnt[a] + 1
        end
        j == n && (mR = a)                          # 当场记录 z 的接收机（事后 argmin 是错的）
        load[a] += pn[j]; cnt[a] += 1
    end
    (isfb[n] && isfb[n-1]) || return nothing
    load_pre = copy(load); load_pre[mR] -= z
    maxload_pre = maximum(load_pre)
    final = load[mR]
    push!(rec, (final = final, z = z, τ = τ,
                marginA = maxload_pre - (2z + 0.4),
                marginB = recv_load - (2z + 0.4),
                min_pre = load_pre[mR], p4 = pn[4], p1 = pn[1],
                cnts = sort(copy(cnt)), recv_cnt = recv_cnt,
                branchA = true, pn = copy(pn)))
    return nothing
end

function main()
    rng = MersenneTwister(7)
    rec = Any[]
    # 临界实例本身（精确复核 final = 1.2）
    probe(PCRIT; rec)
    # 扰动采样：多档噪声
    for (amp, N) in ((0.01, 40000), (0.03, 80000), (0.06, 120000), (0.10, 120000))
        for _ in 1:N
            p = PCRIT .+ (rand(rng, 10) .- 0.5) .* 2 .* amp
            any(x -> x <= 0.02, p) && continue
            sort!(p; rev = true)
            cs = opt_makespan(p, 4)
            probe(p ./ cs; rec)
        end
    end
    println("分支A实例总数 = ", length(rec))
    sort!(rec; by = r -> -r.final)
    nshow = min(25, length(rec))
    println("final 最高的 $(nshow) 条：")
    @printf("%3s %8s %6s %6s %8s %8s %8s %6s %6s %s %s\n", "#", "final", "z", "τ", "marginA", "marginB", "min_pre", "p1", "p4", "cnts", "recv_cnt")
    for i in 1:nshow
        r = rec[i]
        @printf("%3d %8.5f %6.4f %6.4f %8.5f %8.5f %8.5f %6.4f %6.4f %s %d\n",
                i, r.final, r.z, r.τ, r.marginA, r.marginB, r.min_pre, r.p1, r.p4, r.cnts, r.recv_cnt)
    end
    # 统计：final > 1.18 的实例里 marginA/B 最小值、τ−(2z+0.4) 最大值、件数分布
    nf = filter(r -> r.final > 1.18, rec)
    println("\n近失败(final>1.18) = ", length(nf), " 条")
    if !isempty(nf)
        println("  min marginA = ", minimum(r.marginA for r in nf))
        println("  min marginB = ", minimum(r.marginB for r in nf))
        println("  max τ−(2z+0.4) = ", maximum(r.τ - (2r.z + 0.4) for r in nf))
        println("  min p4 = ", minimum(r.p4 for r in nf), "  max p1 = ", maximum(r.p1 for r in nf))
        ch = Dict{Vector{Int},Int}()
        for r in nf; ch[r.cnts] = get(ch, r.cnts, 0) + 1; end
        println("  件数分布：", sort!(collect(ch); by = x -> -x[2]))
        rh = Dict{Int,Int}()
        for r in nf; rh[r.recv_cnt] = get(rh, r.recv_cnt, 0) + 1; end
        println("  接收机件数分布：", sort!(collect(rh); by = x -> -x[2]))
    end
end

main()
