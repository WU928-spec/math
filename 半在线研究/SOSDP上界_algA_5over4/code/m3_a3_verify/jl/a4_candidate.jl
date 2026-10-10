# a4_candidate.jl —— 候选 m=4 算法 A4-c 的聚焦经验评估（无证明）
include("a4_lib.jl")

const A4C      = A4(C_TARGET, :L0,  false, false)   # 候选主形：cap = c·max{p1,p4+p5}，best-fit + fallback
const A4C_SLOT = A4(C_TARGET, :L0,  true,  false)   # 加"M1 补一件"槽规则
const A4C_BR   = A4(C_TARGET, :L0,  true,  true)    # A3 式双分支
const ALGO_A   = A4(5/4,      :p45, false, false)   # 对照：Algorithm A（m=4）

println("="^92)
println("A. 在已知最坏家族（m=4 下界构造）上的表现")
println("="^92)
r = (2 + sqrt(37)) / 11; s = (13 + sqrt(37)) / 33
inst = vcat(fill(1.0, 3), fill(r, 3), fill(s, 3))
println("实例 (1,1,1,r,r,r,s,s,s)，r=", round(r, digits = 4), " s=", round(s, digits = 4))
println("  C* = ", round(opt_makespan(inst, 4), digits = 6))
for (nm, a) in [("A4-c", A4C), ("A4-c+slot", A4C_SLOT), ("A4-c+branch", A4C_BR), ("Algorithm A(5/4)", ALGO_A)]
    println("  ", rpad(nm, 18), " A4 值 = ", round(a4_sim(inst, a)[1], digits = 6),
            "   比值 = ", round(ratio(inst, a), digits = 6))
end

println("\n" * "="^92)
println("B. 大规模随机搜索（每格 800 样本；n=5..12；家族 pow/blocks/two/tight/general）")
println("="^92)
families = (:pow, :blocks, :two, :tight, :general)
function big_search(a::A4; per = 800, nrange = 5:12, seed = 99)
    rng = MersenneTwister(seed); worst = 0.0; wit = Float64[]; wn = 0
    for n in nrange, fam in families
        for _ in 1:per
            p = gen_instance(n, rng; family = fam, lower = fam == :general ? 0.0 : ALPHA + 1e-9)
            r = ratio(p, a)
            r > worst && (worst = r; wit = copy(p); wn = n)
        end
    end
    return worst, wit, wn
end
for (nm, a) in [("A4-c", A4C), ("A4-c+slot", A4C_SLOT), ("A4-c+branch", A4C_BR)]
    t0 = time()
    w, p, n = big_search(a)
    println(rpad(nm, 16), " 最坏比值 = ", rpad(round(w, digits = 6), 10),
            " n = ", lpad(n, 3), "   ", (w <= C_TARGET + 1e-9 ? "✓ <= c" : "✗ > c"),
            "   (", round(time() - t0, digits = 1), "s)")
    println("     见证 p = ", round.(p, digits = 4))
end
println("\n注：以上为经验搜索（下界方向证据）；未找到反例 ≠ 已证 c-竞争。")
