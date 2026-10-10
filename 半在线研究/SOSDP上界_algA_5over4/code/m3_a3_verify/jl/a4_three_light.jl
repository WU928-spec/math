# a4_three_light.jl —— 数值验证目标不等式
#   目标引理（经推导与临界实例取等确认）：
#     当最后一件 z = p_n 是"兜底"放置时，放它**之前**，"三台最轻机器的负载之和" ≤ 3.6 − 3z
#   （若成立 ⟹ min ≤ (三轻之和)/3 ≤ 1.2 − z ⟹ 最终 = min + z ≤ 6/5。临界实例恰取等：2.7 = 3.6 − 0.9）
include("a4_lib.jl")
using Random

function check(n, N, seed)
    rng = MersenneTwister(seed); worst = -Inf; worstp = Float64[]; nviol = 0; nfb = 0
    a4 = A4(C_TARGET, [:p1, :p45], false, false)
    for _ in 1:N
        p = sort(Float64[rand(rng, 1:20) / 20 for _ in 1:n]; rev = true)
        cs = opt_makespan(p, 4); pn = p ./ cs
        minimum(pn) < 4 / 15 - 1e-12 && continue
        # 重放轨迹，记录"放 z 之前"的负载
        load = zeros(4)
        Λ = max(pn[1], pn[4] + pn[5]); τ = C_TARGET * Λ
        isfb = Bool[]; put(j, m) = (load[m] += pn[j])
        mR = 0
        for j in 1:min(4, n); put(j, j); end
        for j in 5:n
            E = [m for m in 1:4 if load[m] + pn[j] <= τ + 1e-15]
            push!(isfb, isempty(E))
            aj = isempty(E) ? argmin(load) : E[argmax(load[E])]
            j == n && (mR = aj)                     # 当场记录 z 的接收机
            put(j, aj)
        end
        z = pn[n]
        isfb[end] || continue                       # 只要最后一步是兜底的实例
        nfb += 1
        # 放 z 前的负载 = 重放第 n 步时**当场记录**的接收机减 z
        # （事后 argmin 是错的：放完 z 后接收机可能已不是最轻机，
        #   如临界实例放完 M1=1.2、argmin 变成 M2/M3 —— 2026-10-08 bug 修正）
        load_pre = copy(load); load_pre[mR] -= z
        three = sort(load_pre)[1:3]
        s3 = sum(three)
        lhs = s3 - (3.6 - 3z)
        if lhs > 1e-9
            nviol += 1
            lhs > worst && (worst = lhs; worstp = copy(pn))
        end
    end
    println("n=", n, "  兜底实例 ", nfb, "  违反『三轻 ≤ 3.6−3z』 ", nviol, "  条")
    worst > -Inf && println("   最坏超出量 = ", round(worst, digits = 5), "  实例 = ", round.(worstp, digits = 4))
end

for n in 9:12
    check(n, 80000, 42)
end
