include("a4_lib.jl")

# 两个新机制（都建立在 cap=c·Λ 之上）
#  M1「留一台最轻机」：E 里排除当前最轻的那台（把它留给后续小件）；E 无可选时退回全局最轻。
#  M4「一次拒绝即转 LPT」：先用 cap 规则；一旦发生"没有任何机器能装下"（触发 fallback），
#                          从此以后全部按 LPT（最轻机）走。
function a4_mech(p::Vector{Float64}, kind::Symbol, rho = C_TARGET)
    n = length(p); load = zeros(4); asg = [Int[] for _ in 1:4]
    put(j, m) = (load[m] += p[j]; push!(asg[m], j))
    for j in 1:min(4, n); put(j, j); end
    n <= 4 && return maximum(load)
    Λ = coord_value(p, [:p1, :p45]); τ = rho * Λ
    lpt = false
    for j in 5:n
        E = [m for m in 1:4 if load[m] + p[j] <= τ]
        if kind == :M4 && lpt
            put(j, argmin(load)); continue
        end
        if isempty(E)
            kind == :M4 && (lpt = true)
            put(j, argmin(load))
        else
            if kind == :M1
                lite = argmin(load)
                E2 = setdiff(E, [lite])
                put(j, isempty(E2) ? lite : E2[argmax(load[E2])])
            else
                put(j, E[argmax(load[E])])
            end
        end
    end
    return maximum(load)
end
rmech(p, kind; rho = C_TARGET) = a4_mech(p, kind, rho) / opt_makespan(p, 4)

function attack_mech(kind::Symbol; rho = C_TARGET, nset = 8:12, restarts = 40, rounds = 250, seed = 2026)
    rng = MersenneTwister(seed); best = 0.0; bp = Float64[]; bn = 0
    for _ in 1:restarts
        n = rand(rng, nset)
        p = gen_instance(n, rng; family = rand(rng, (:pow, :blocks, :two, :tight, :general)),
                         lower = rand(rng) < 0.7 ? ALPHA + 1e-9 : 0.0)
        cur = rmech(p, kind; rho = rho)
        for _ in 1:rounds
            imp = false
            for i in eachindex(p)
                for ε in (-0.25, -0.12, -0.05, -0.02, 0.02, 0.05, 0.12, 0.25, 0.6)
                    q = copy(p); q[i] = max(q[i] * (1 + ε), 0.0); sort!(q; rev = true)
                    r = rmech(q, kind; rho = rho)
                    r > cur + 1e-10 && (cur = r; p = q; imp = true)
                end
            end
            for i in 1:length(p)
                for ε in (-0.2, -0.08, 0.08, 0.2)
                    q = copy(p); q[i:end] .*= (1 + ε); sort!(q; rev = true)
                    r = rmech(q, kind; rho = rho)
                    r > cur + 1e-10 && (cur = r; p = q; imp = true)
                end
            end
            imp || break
        end
        cur > best && (best = cur; bp = copy(p); bn = length(p))
    end
    return best, bp, bn
end

px = [0.8694, 0.7341, 0.7203, 0.5947, 0.5883, 0.5871, 0.4412, 0.4288, 0.4273, 0.4267]
println("诊断实例上的比值：M1 = ", round(rmech(px, :M1), digits = 5),
        "；M4 = ", round(rmech(px, :M4), digits = 5), "；LPT = 1.10518；c = ", round(C_TARGET, digits = 5))
println("-"^80)
for kind in (:M1, :M4)
    w, p, n = attack_mech(kind)
    println(rpad(string(kind), 6), " 攻击最坏比值 = ", rpad(round(w, digits = 6), 10), " n=", lpad(n, 2),
            "   ", (w <= C_TARGET + 1e-9 ? "✓ 未破 c" : "✗ 破 c"))
    println("       p = ", round.(p, digits = 4))
end
