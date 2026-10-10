# a4_attack.jl —— 对候选 m=4 算法做定向爬山攻击（最大化比值），检验是否能把比值推过 c
include("a4_lib.jl")

"对给定算法做坐标爬山：多起点、多尺度扰动、块级缩放"
function attack(a::A4; nset = 8:12, restarts = 40, rounds = 250, seed = 2026)
    rng = MersenneTwister(seed)
    best = 0.0; bp = Float64[]; bn = 0
    for trial in 1:restarts
        n = rand(rng, nset)
        # 起点：混合分布
        p = gen_instance(n, rng; family = rand(rng, (:pow, :blocks, :two, :tight, :general)),
                         lower = rand(rng) < 0.7 ? ALPHA + 1e-9 : 0.0)
        cur = ratio(p, a)
        for _ in 1:rounds
            improved = false
            for i in eachindex(p)
                for ε in (-0.25, -0.12, -0.05, -0.02, 0.02, 0.05, 0.12, 0.25, 0.6)
                    q = copy(p); q[i] = max(q[i] * (1 + ε), 0.0)
                    sort!(q; rev = true)
                    r = ratio(q, a)
                    if r > cur + 1e-10
                        cur = r; p = q; improved = true
                    end
                end
            end
            # 块级：把某个下标起的后缀整体缩放（模拟"若干等值块"）
            for i in 1:length(p)
                for ε in (-0.2, -0.08, 0.08, 0.2)
                    q = copy(p); q[i:end] .*= (1 + ε); sort!(q; rev = true)
                    r = ratio(q, a)
                    if r > cur + 1e-10
                        cur = r; p = q; improved = true
                    end
                end
            end
            improved || break
        end
        if cur > best
            best = cur; bp = copy(p); bn = length(p)
        end
    end
    return best, bp, bn
end

println("="^92)
println("定向爬山攻击：目标 = 最大化 C_A4 / C*（越接近或超过 c 越危险）")
println("="^92)
cands = [
  ("B1 coords{p1,p45,p56}",              A4(C_TARGET, [:p1,:p45,:p56],        false, false)),
  ("B2 coords{p1,p45,p56,m56_345}",      A4(C_TARGET, [:p1,:p45,:p56,:min56_345], false, false)),
  ("B3 coords{p1,p45}+branch(fixed)",    A4(C_TARGET, [:p1,:p45],             false, true)),
  ("B4 coords{p1,p45,p56}+slot",         A4(C_TARGET, [:p1,:p45,:p56],        true,  false)),
  ("B5 coords{p1,p45,p56}+slot+branch",  A4(C_TARGET, [:p1,:p45,:p56],        true,  true)),
  ("对照 A4-c 朴素(cap=c)",               A4(C_TARGET, [:p1,:p45],             false, false)),
  ("对照 ρ=5/4",                          A4(5/4,      [:p1,:p45],             false, false)),
]
println("="^96)
println("定向爬山攻击（修正 branch bug + 更强坐标族）：目标 = 最大化 C_A4/C*")
println("="^96)
for (nm, a) in cands
    t0 = time()
    w, p, n = attack(a)
    verdict = w > C_TARGET + 1e-9 ? "✗ 超过 c（反例）" : "✓ 未超过 c"
    println(rpad(nm, 36), " max=", rpad(round(w, digits = 6), 10), " n=", lpad(n, 2), "  ", verdict,
            "  (", round(time() - t0, digits = 1), "s)")
    println("      p = ", round.(p, digits = 4))
end
