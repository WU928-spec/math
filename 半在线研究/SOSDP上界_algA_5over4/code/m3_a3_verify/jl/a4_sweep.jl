include("a4_lib.jl")
# 诊断实例（攻击找出的反例）
px = [0.8694, 0.7341, 0.7203, 0.5947, 0.5883, 0.5871, 0.4412, 0.4288, 0.4273, 0.4267]
println("诊断实例：C* = ", round(opt_makespan(px, 4), digits = 6),
        "；LPT 比值 = ", round((begin
              l = zeros(4); for x in px; l[argmin(l)] += x; end; maximum(l)
          end) / opt_makespan(px, 4), digits = 6))
println("-"^88)
println(rpad("ρ", 10), rpad("coord", 16), lpad("该实例比值", 11), lpad("攻击最坏", 11), "   结论")
for (ρ, cs) in [(1.00, [:p1,:p45]), (1.05, [:p1,:p45]), (1.10, [:p1,:p45]), (1.15, [:p1,:p45]),
                (C_TARGET, [:p1,:p45]), (1.20, [:p1,:p45]), (5/4, [:p1,:p45])]
    a = A4(ρ, cs, false, false)
    r0 = ratio(px, a)
    w, _, _ = attack(a; restarts = 25, rounds = 200, seed = 4242)
    println(rpad(round(ρ, digits = 6), 10), rpad(string(cs), 16), lpad(round(r0, digits = 5), 11),
            lpad(round(w, digits = 5), 11), "   ", (w <= C_TARGET + 1e-9 ? "✓ 攻击未破 c" : "✗ 破 c"))
end
