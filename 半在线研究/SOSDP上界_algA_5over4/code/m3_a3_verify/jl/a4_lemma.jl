# a4_lemma.jl —— 轨迹空间的结构性削减：可证引理 + 削减后规模量化
include("a4_lib.jl")
using JuMP, HiGHS
const RHO = C_TARGET          # 算法的 cap 倍率
const RHO_T = 1.2             # **证明目标**（6/5）——引理里的 ρ 指目标

println("="^90)
println("L1/L2：目标 ρ = ", round(RHO, digits = 6), " 下的可证引理（反例设定：极小反例、C* = 1、z = p_n 首个失败工件）")
println("="^90)
m = 4
α2 = (m / (m - 1)) * (RHO_T - 1)          # 由 ℓ_min ≤ (m - z)/m 与 ℓ_min + z > ρ 推出 z > m(ρ-1)/(m-1)
println("L1（工件下界）：z > m(ρ-1)/(m-1) = ", round(α2, digits = 6), "  （目标 ρ = ", RHO_T, "）",
        "  > 1/4 ? ", α2 > 0.25)
println("   ⟹ 所有工件 > ", round(α2, digits = 6), " ⟹ 每台**最优**机器至多 ", floor(Int, 1 / α2),
        " 件 ⟹ n ≤ ", m * floor(Int, 1 / α2))
kmax = floor(Int, RHO_T / α2)
println("L2（算法机件数）：失败前每台算法机负载 ≤ ρ ⟹ 每台至多 floor(ρ/α') = ", kmax, " 件")
println("L3（值坐标冻结）：τ = ρ·max{p1, p4+p5} 在 p5 到达后即固定；负载单调不减。")
println("L4（≤2 件机器）：含 p1 的 ≤2 件机器负载 ≤ p1 + p5；不含 p1 的 ≤2 件机器负载 ≤ max{p2+p5, p3+p4, p4+p5}。")

println("\n", "="^90)
println("削减后的规模量化（n ≤ 12，每台算法机 ≤ ", kmax, " 件，含开局 4 件）")
println("="^90)
"分配模式数：把 n-4 个后续工件分到 4 台机、每台额外 ≤ kmax-1 件"
function profile_count(n, extra_max)
    # 计算 (k1..k4) 每台额外件数 ≤ extra_max、和 = n-4 的有序分配数 Σ n!/(Π(1+ki)!)
    tot = 0; comps = 0
    e = n - 4
    e < 0 && return (0, 0)
    function rec(rem, ki, acc)
        if ki == 4
            if rem <= extra_max
                push!(acc, vcat(acc === nothing ? Int[] : Int[], rem))
            end
            return
        end
        for k in 0:min(rem, extra_max); rec(rem - k, ki + 1, acc); end
    end
    # 直接枚举四元组
    cnt = 0; ways = 0
    for k1 in 0:extra_max, k2 in 0:extra_max, k3 in 0:extra_max
        k4 = e - k1 - k2 - k3
        (0 <= k4 <= extra_max) || continue
        cnt += 1
        ways += factorial(e) ÷ (factorial(k1) * factorial(k2) * factorial(k3) * factorial(k4))
    end
    return (cnt, ways)
end
function scale()
    tot_assign = 0; tot_pieces = 0
    for n in 5:12
        c, w = profile_count(n, kmax - 1)
        println("n=", lpad(n, 2), "  额外件数四元组 ", lpad(c, 4), " 个；分配模式（有序）", lpad(w, 7),
                " 个；乘 Λ 分支 2 与最重机 4 ⟹ 片上界 ", lpad(w * 8, 8))
        tot_assign += w; tot_pieces += w * 8
    end
    println("合计：分配模式 ", tot_assign, "；片数上界（×8）", tot_pieces)
    println("（对照：未用 L2 时 Σ4^(n-4) = ", sum(4^(n - 4) for n in 5:12), "）")
    println("\n每片一次 LP（内含全部装箱）：n=10 约 11 s、n=12 约 25 s ⟹ 全量约 ",
            round(tot_pieces * 15 / 3600, digits = 1), " 单核小时")

end
scale()
