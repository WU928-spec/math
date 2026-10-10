# tests_m4_coords.jl —— m=4 候选"值坐标"（C* 下界）筛选
# 判据：该表达式在"4 台机器、每台 <=3 件、负载 <=1、所有工件 > alpha"的全体非增实例上，最大值 <= 1。
# 关键优化（单调性）：坐标只用到下标 1..k 时，最大值必在 n = k 处取到
#   （把 n>k 的可行实例丢掉尾部工件，仍是可行实例且坐标值不变）。
include("common.jl")

coords = [
    ("p1",                     [term((1, 1.0))]),
    ("p4+p5",                  [term((4, 1.0), (5, 1.0))]),
    ("p3+p4",                  [term((3, 1.0), (4, 1.0))]),
    ("p2+p5",                  [term((2, 1.0), (5, 1.0))]),
    ("p2+p6",                  [term((2, 1.0), (6, 1.0))]),
    ("p5+p6",                  [term((5, 1.0), (6, 1.0))]),
    ("p3+p4+p5",               [term((3, 1.0), (4, 1.0), (5, 1.0))]),
    ("p4+p5+p6",               [term((4, 1.0), (5, 1.0), (6, 1.0))]),
    ("p2+p5+p6",               [term((2, 1.0), (5, 1.0), (6, 1.0))]),
    ("min{p2+p5,p3+p4+p5}",    [term((2, 1.0), (5, 1.0)), term((3, 1.0), (4, 1.0), (5, 1.0))]),
    ("min{p2+p6,p3+p5+p6}",    [term((2, 1.0), (6, 1.0)), term((3, 1.0), (5, 1.0), (6, 1.0))]),
    ("min{p2+p6,p4+p5+p6}",    [term((2, 1.0), (6, 1.0)), term((4, 1.0), (5, 1.0), (6, 1.0))]),
    ("min{p5+p6,p3+p4+p5}",    [term((5, 1.0), (6, 1.0)), term((3, 1.0), (4, 1.0), (5, 1.0))]),
    ("min{p3+p5,p4+p5+p6}",    [term((3, 1.0), (5, 1.0)), term((4, 1.0), (5, 1.0), (6, 1.0))]),
    ("p7+p8+p9",               [term((7, 1.0), (8, 1.0), (9, 1.0))]),
]

maxidx(o::Vector{Row}) = maximum(maximum(i for (i, _) in r) for r in o)

println("m=4 坐标筛选（4 台机器、每台 <=3 件、负载 <=1、所有工件 > alpha = ",
        round(ALPHA, digits = 6), "）")
println("单调性：坐标用到下标 <=k 时取 n=k 即可")
println("-"^84)
println(rpad("候选坐标", 24), lpad("n", 4), lpad("结构数", 9), lpad("最大值", 11), "   可作坐标?")
for (name, terms) in coords
    n = maxidx(terms)
    parts = partitions(n, 3, 4)
    res = solve_lp(n = n, parts = parts, objectives = [terms])
    v, p = res[1]
    println(rpad(name, 24), lpad(n, 4), lpad(length(parts), 9), lpad(round(v, digits = 6), 11),
            "   ", (v <= 1 + 1e-9 ? "是 ✓" : "否 ✗"))
    v > 1 + 1e-9 && println("       见证 p = ", round.(p, digits = 4))
end
println("\n（“是” = 该表达式恒 <= C*，可直接用作 m=4 算法 cap 的坐标）")
