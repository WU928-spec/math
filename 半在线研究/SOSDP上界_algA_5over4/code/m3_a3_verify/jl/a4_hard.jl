include("a4_lib.jl")
# 对 A4-c 做加强攻击：多 seed × 多重启 × 更多轮，n=8..12
function hard()
    a = A4(C_TARGET, [:p1, :p45], false, false)
    best = 0.0; bp = Float64[]; bn = 0
    for seed in (1, 7, 2026, 31337, 99991)
        w, p, n = attack(a; nset = 8:12, restarts = 60, rounds = 350, seed = seed)
        println("seed ", lpad(seed, 6), "：最坏 ", round(w, digits = 6), "  n=", lpad(n, 2),
                "   p=", round.(p, digits = 4))
        w > best && (best = w; bp = copy(p); bn = n)
    end
    println("-"^84)
    println("A4-c 加强攻击总最坏 = ", round(best, digits = 6), "  (n=", bn, ")")
    println("  相对 c    = ", round(best / C_TARGET, digits = 4), " ×c")
    println("  相对 5/4  = ", round(best / 1.25, digits = 4), " ×(5/4)   ",
            best < 1.25 ? "→ 未触及 5/4 ✓" : "→ 已超过 5/4 ✗")
    println("  最好实例 p = ", round.(bp, digits = 4))
    # 同实例上对照 LPT
    l = zeros(4); for x in bp; l[argmin(l)] += x; end
    println("  该实例上 LPT 比值 = ", round(maximum(l) / opt_makespan(bp, 4), digits = 6))

end
hard()
