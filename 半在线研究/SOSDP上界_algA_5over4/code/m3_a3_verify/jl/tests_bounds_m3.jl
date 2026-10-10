# tests_bounds_m3.jl —— 复现文档 §6 表：m=3 单条数值界（O5 各条 + 引理 2 + 引理 1 的两个加强形式）
# 以及 §4.1(i) 的适用性检验（n9 失败设定）
include("common.jl")

println("="^78)
println("A. m=3 单条数值界（3 台机器、每台 <=3 件、负载 <=1、所有工件 > alpha）")
println("="^78)

struct Item; name::String; n::Int; terms::Vector{Row}; ref::Float64; note::String; end

items = [
    Item("p3",            7, [term((3,1.0))],                       0.5,  "<= 1/2"),
    Item("p7",            7, [term((7,1.0))],                       1/3,  "<= 1/3"),
    Item("p6+p7",         7, [term((6,1.0),(7,1.0))],               2/3,  "<= 2/3"),
    Item("p3+p6+p7",      7, [term((3,1.0),(6,1.0),(7,1.0))],       7/6,  "<= 7/6（O6 段用）"),
    Item("p2",            8, [term((2,1.0))],                       0.5,  "<= 1/2"),
    Item("p5+p8",         8, [term((5,1.0),(8,1.0))],               2/3,  "<= 2/3"),
    Item("p2+p5+p8",      8, [term((2,1.0),(5,1.0),(8,1.0))],       7/6,  "<= 7/6 < c（O6 段用）"),
    Item("p2+p6",         8, [term((2,1.0),(6,1.0))],               C_TARGET, "<= c（Case 1 用）"),
    Item("p4+p9",         9, [term((4,1.0),(9,1.0))],               2/3,  "<= 2/3（引理 2）"),
    Item("p3+p4+p9",      9, [term((3,1.0),(4,1.0),(9,1.0))],       1.0,  "<= 1"),
    Item("p1+p8+p9",      9, [term((1,1.0),(8,1.0),(9,1.0))],       1.0,  "<= 1"),
    Item("p1+p4+p9",      9, [term((1,1.0),(4,1.0),(9,1.0))],       1 - 2*ALPHA + 2/3, "<= 1-2z+2/3（失败设定用）"),
    # 引理 1 的 L 部分：min{p2+p5, p3+p4+p5} <= C*
    Item("min{p2+p5,p3+p4+p5}", 9, [term((2,1.0),(5,1.0)), term((3,1.0),(4,1.0),(5,1.0))], 1.0, "<= C*（引理 1 的 L 部分）"),
]

for n in unique([it.n for it in items])
    parts = partitions(n, 3, 3)
    sel = findall(it -> it.n == n, items)
    res = solve_lp(n = n, parts = parts, objectives = [items[i].terms for i in sel])
    println("\n-- n = $n（结构数 $(length(parts))）")
    for (k, i) in enumerate(sel)
        report(items[i].name, res[k][1], items[i].ref)
        println("      ", rpad("原文/用途: " * items[i].note, 34),
                "argmax p = ", round.(res[k][2], digits = 4))
    end
end

# 引理 1 / Case 1 / Case 2 的三个"条件化"最大（需 <= 1）
println("\n" * "="^78)
println("B. 引理 1 的两个加强形式（条件化）")
println("="^78)
for (nm, n, extra, terms, ref) in [
        ("Case1: p2>=p3+p4 下 p3+p4+p5", 7, [(term((2,-1.0),(3,1.0),(4,1.0)), 0.0)],
         [term((3,1.0),(4,1.0),(5,1.0))], "<= C*（Case 1 用）"),
        ("Case2: p2<=p3+p4 下 p2+p5",    7, [(term((2,1.0),(3,-1.0),(4,-1.0)), 0.0)],
         [term((2,1.0),(5,1.0))], "<= C*（Case 2 用）")]
    res = solve_lp(n = n, parts = partitions(n, 3, 3), objectives = [terms], extra = extra)
    report(nm, res[1][1], 1.0)
    println("      ", rpad(ref, 34), "argmax p = ", round.(res[1][2], digits = 4))
end

# ---------------------------------------------------------------- n9 失败设定检验
println("\n" * "="^78)
println("C. §4.1(i) 适用性：C_A3 <= p1+p4+p9 只在\"z=p_n 是失败工件\"时成立")
println("="^78)


"A3 逐件执行；返回每步后的 (各机工件数, 各机负载) 快照"
function a3_trace_cnt(p::Vector{Float64})
    n = length(p); load = zeros(3); cnt = zeros(Int, 3); snaps = Tuple{Vector{Int},Vector{Float64}}[]
    function put(j, m)
        load[m] += p[j]; cnt[m] += 1; push!(snaps, (copy(cnt), copy(load)))
    end
    put(1, 1); put(2, 2); put(3, 3)
    if n > 3
        L0 = max(p[1], p[3] + p[4])
        if p[1] + p[4] <= C_TARGET * L0
            put(4, 1)
            if n > 4
                put(5, 2)
                for j in 6:n
                    put(j, argmin(load))
                end
            end
        else
            put(4, 3)
            if n > 4
                L = max(L0, min(p[2] + p[5], p[3] + p[4] + p[5]))
                for j in 5:n
                    if cnt[1] == 1 && p[1] + p[j] <= C_TARGET * L
                        put(j, 1)
                    else
                        put(j, argmin(load))
                    end
                end
            end
        end
    end
    return snaps
end

"A3 逐件执行；返回 (每步后的负载快照, 最终 makespan)"
function a3_trace(p::Vector{Float64})
    n = length(p); load = zeros(3); cnt = zeros(Int, 3); snaps = Vector{Vector{Float64}}()
    function put(j, m)
        load[m] += p[j]; cnt[m] += 1; push!(snaps, copy(load))
    end
    put(1, 1); put(2, 2); put(3, 3)
    if n > 3
        L0 = max(p[1], p[3] + p[4])
        if p[1] + p[4] <= C_TARGET * L0
            put(4, 1)
            if n > 4
                put(5, 2)
                for j in 6:n
                    put(j, argmin(load))
                end
            end
        else
            put(4, 3)
            if n > 4
                L = max(L0, min(p[2] + p[5], p[3] + p[4] + p[5]))
                for j in 5:n
                    if cnt[1] == 1 && p[1] + p[j] <= C_TARGET * L
                        put(j, 1)
                    else
                        put(j, argmin(load))
                    end
                end
            end
        end
    end
    return snaps
end

"z = p_n 是否为'第一个'使某机负载 > c 的工件"
function last_job_is_first_failure(p)
    snaps = a3_trace(p); n = length(p)
    before = n >= 2 ? snaps[n-1] : zeros(3)
    return maximum(before) <= C_TARGET && maximum(snaps[n]) > C_TARGET
end

# §4.1(i) 的结构检验（非空洞版）：
#  (1) 引理 G′：任何时刻 ℓ(M1) <= p1+p4
#  (2) 若 z=p_n 的放置使该机成为最终最大负载机，则 C_A3 = ℓ_min + p_n（即 §4.1(i) 的等式）
#  (3) 反例计数：是否存在 C_A3 > c·C* 的实例（A3 是 c-竞争 ⟹ 预期 0 个）
# 引理 G(ii) 与 §4.1(i) 的结构检验（这是文档早期版本出错、被本测试纠正的地方）
#  (1) 引理 G(ii)：任何时刻，凡"至多含 2 个工件"的机器，其负载 <= p1+p4
#  (2) 8 件已放（n=9、z=p9 到来前）时，存在 ≤2 件且负载 <= p1+p4 的机器（= 原文那句断言）
#  (3) 若 z 的放置使其机器成为最终最大负载机，则 C_A3 = ℓ_min + p_n（§4.1(i) 的等式）
#  (4) 反例计数：是否存在 C_A3 > c·C* 的实例（A3 是 c-竞争 ⟹ 预期 0 个）
function structural_checks(samples = 4000)
    rng = MersenneTwister(5)
    bad_G = 0; bad_claim = 0; bad_eq = 0; counterexamples = 0; eq_tested = 0
    for _ in 1:samples
        p = rand_instance(9, rng; normalize = false)
        snaps = a3_trace_cnt(p)
        cstar = brute_opt(p, 3)
        b = p[1] + p[4]
        # (1) 引理 G(ii)
        for (cnt, load) in snaps
            for i in 1:3
                if cnt[i] <= 2 && load[i] > b + 1e-12
                    bad_G += 1
                end
            end
        end
        # (2) z 到来前（8 件）的断言
        cnt8, load8 = snaps[8]
        any(i -> cnt8[i] <= 2 && load8[i] <= b + 1e-12, 1:3) || (bad_claim += 1)
        # (3) 等式
        before, after = load8, snaps[9][2]
        if maximum(after) > maximum(before) + 1e-12
            eq_tested += 1
            abs(maximum(after) - (minimum(before) + p[9])) > 1e-9 && (bad_eq += 1)
        end
        # (4) 反例
        maximum(after) > C_TARGET * cstar + 1e-9 && (counterexamples += 1)
    end
    println("(1) 引理 G(ii) 违例数（≤2 件机器负载 <= p1+p4）：", bad_G, "   （应为 0）")
    println("(2) 原文断言违例数（8 件后存在 ≤2 件且负载 <= p1+p4 的机器）：", bad_claim, "   （应为 0）")
    println("(3) \"末件成为新最大\" 的样本数：", eq_tested, "；其中 C_A3 = ℓ_min+p_n 不成立者：", bad_eq, "   （应为 0）")
    println("(4) 比值意义下的反例数（C_A3 > c·C*）：", counterexamples, "   （应为 0）")
end
structural_checks()
