# a4_lemmaO_check.jl —— 数值检验引理 O 的两种形式（分支 A：步 n-1 与步 n 均兜底）
#   形式 A（较弱，=引理 O 本身）：放 z 前 maxload ≥ 2z + 2/5
#   形式 B（较强）：步 n-1 的兜底接收机新负载 q_r + p_{n-1} ≥ 2z + 2/5
#   另检验：失败 ⟹ τ < 2z + 2/5（已手证，做 sanity check）；以及 p4 ≥ 2/5 的猜测
include("a4_lib.jl")
using Random, Printf

function check(n, N, seed)
    rng = MersenneTwister(seed)
    nA = 0                       # 分支 A 实例数
    minA_all = Inf; minB_all = Inf          # 全体分支 A 上的最小余量（形式 A/B）
    minA_nf = Inf; minB_nf = Inf            # 近失败（final > 1.18）上的最小余量
    nkill = 0; nfail = 0; ntauviol = 0; np4viol = 0
    worst_inst = Float64[]; worst_final = -Inf
    p4min_nf = Inf
    for _ in 1:N
        p = sort(Float64[rand(rng, 1:20) / 20 for _ in 1:n]; rev = true)
        cs = opt_makespan(p, 4); pn = p ./ cs
        z = pn[n]
        load = zeros(4)
        Λ = max(pn[1], pn[4] + pn[5]); τ = C_TARGET * Λ
        isfb = falses(n)
        q_r = NaN; recv_load = NaN; mR = 0
        for j in 1:4; load[j] += pn[j]; end
        for j in 5:n
            E = [m for m in 1:4 if load[m] + pn[j] <= τ + 1e-15]
            fb = isempty(E)
            isfb[j] = fb
            if j == n - 1 && fb
                q_r = minimum(load)
                recv_load = q_r + pn[j]
            end
            a = fb ? argmin(load) : E[argmax(load[E])]
            j == n && (mR = a)                      # 当场记录 z 的接收机（事后 argmin 是错的）
            load[a] += pn[j]
        end
        (isfb[n] && isfb[n-1]) || continue          # 只要分支 A
        nA += 1
        # 放 z 前负载：接收机减 z
        load_pre = copy(load); load_pre[mR] -= z
        maxload_pre = maximum(load_pre)
        final = load[mR]                            # = min_pre + z
        marginA = maxload_pre - (2z + 0.4)
        marginB = recv_load - (2z + 0.4)
        minA_all = min(minA_all, marginA); minB_all = min(minB_all, marginB)
        if final > 1.18
            minA_nf = min(minA_nf, marginA); minB_nf = min(minB_nf, marginB)
            p4min_nf = min(p4min_nf, pn[4])
            τ >= 2z + 0.4 - 1e-12 && (ntauviol += 1)
            pn[4] < 0.4 - 1e-12 && (np4viol += 1)
        end
        if final > 6 / 5 + 1e-9
            nkill += 1
            if final > worst_final
                worst_final = final; worst_inst = copy(pn)
            end
        end
        final > 6 / 5 - 1e-9 && (nfail += 1)
    end
    @printf("n=%d  分支A %d 条 | 全体: minA=%.5f minB=%.5f | 近失败(>1.18): minA=%.5f minB=%.5f p4min=%.4f | τ违规 %d p4违规 %d | 达6/5 %d 超6/5 %d\n",
            n, nA, minA_all, minB_all, minA_nf, minB_nf, p4min_nf, ntauviol, np4viol, nfail, nkill)
    nkill > 0 && println("   最坏实例 = ", round.(worst_inst, digits = 4))
end

for n in 9:12
    check(n, 40000, 42)
end
