# a4_compare.jl —— 五条候选规则在**同一攻击预算**下的正面对比
# 规则：
#   A4c : cap = c·max{p1,p4+p5}；E≠∅ → E 中最满；否则 → 最轻机
#   M1  : 同上，但 E 中排除"当前最轻机"（留一台最轻机给后续）
#   M4  : 同上，但一旦发生一次"无处可放"，此后全部走最轻机（LPT）
#   S1  : A3 式——M1 只含 p1 且过 cap → 补 M1；否则 → 最轻机（无 best-fit）
#   H2  : cap 取 min(c·max{p1,p4+p5}, c·已见总和/4)；E≠∅ → 最满；否则 → 最轻机
include("a4_lib.jl")

function rule(p::Vector{Float64}, kind::Symbol, rho = C_TARGET)
    n = length(p); load = zeros(4); cnt = zeros(Int, 4)
    put(j, m) = (load[m] += p[j]; cnt[m] += 1)
    for j in 1:min(4, n); put(j, j); end
    n <= 4 && return maximum(load)
    Λ0 = max(p[1], p[4] + p[5]); seen = sum(p[1:4]); lpt = false
    for j in 5:n
        seen += p[j]
        τ = kind == :H2 ? min(rho * Λ0, rho * (seen / 4)) : rho * Λ0
        if kind == :M4 && lpt
            put(j, argmin(load)); continue
        end
        E = [m for m in 1:4 if load[m] + p[j] <= τ]
        if isempty(E)
            kind == :M4 && (lpt = true)
            put(j, argmin(load))
        elseif kind == :S1
            if cnt[1] == 1 && p[1] + p[j] <= τ
                put(j, 1)
            else
                put(j, argmin(load))
            end
        elseif kind == :M1
            lite = argmin(load); E2 = setdiff(E, [lite])
            put(j, isempty(E2) ? lite : E2[argmax(load[E2])])
        else
            put(j, E[argmax(load[E])])
        end
    end
    return maximum(load)
end
rr(p, kind; rho = C_TARGET) = rule(p, kind, rho) / opt_makespan(p, 4)

function attack_rule(kind::Symbol; nset = 8:12, restarts = 60, rounds = 350, seeds = (1, 7, 2026, 31337, 99991))
    best = 0.0; bp = Float64[]; bn = 0
    for seed in seeds
        rng = MersenneTwister(seed)
        for _ in 1:restarts
            n = rand(rng, nset)
            p = gen_instance(n, rng; family = rand(rng, (:pow, :blocks, :two, :tight, :general)),
                             lower = rand(rng) < 0.7 ? ALPHA + 1e-9 : 0.0)
            cur = rr(p, kind)
            for _ in 1:rounds
                imp = false
                for i in eachindex(p)
                    for ε in (-0.25, -0.12, -0.05, -0.02, 0.02, 0.05, 0.12, 0.25, 0.6)
                        q = copy(p); q[i] = max(q[i] * (1 + ε), 0.0); sort!(q; rev = true)
                        r = rr(q, kind)
                        r > cur + 1e-10 && (cur = r; p = q; imp = true)
                    end
                end
                for i in 1:length(p)
                    for ε in (-0.2, -0.08, 0.08, 0.2)
                        q = copy(p); q[i:end] .*= (1 + ε); sort!(q; rev = true)
                        r = rr(q, kind)
                        r > cur + 1e-10 && (cur = r; p = q; imp = true)
                    end
                end
                imp || break
            end
            cur > best && (best = cur; bp = copy(p); bn = length(p))
        end
    end
    return best, bp, bn
end

function main()
    px = [0.8694, 0.7341, 0.7203, 0.5947, 0.5883, 0.5871, 0.4412, 0.4288, 0.4273, 0.4267]
    py = [1.0862, 0.9842, 0.9527, 0.7885, 0.7548, 0.6149, 0.6068, 0.5735, 0.5598]
    pz = [0.3664, 0.3481, 0.3157, 0.2923, 0.2611, 0.2385, 0.2047, 0.2022, 0.2022]
    rr2 = (2 + sqrt(37)) / 11; ss = (13 + sqrt(37)) / 33
    low = vcat(fill(1.0, 3), fill(rr2, 3), fill(ss, 3))
    println("同一攻击预算（5 seeds × 60 重启 × 350 轮，n=8..12）")
    println(rpad("规则", 7), lpad("攻击最坏", 10), lpad("n", 4), lpad("×c", 8), lpad("×5/4", 8),
            lpad("px", 8), lpad("py", 8), lpad("pz", 8), lpad("下界家族", 10))
    println("-"^92)
    for kind in (:A4c, :M1, :M4, :S1, :H2)
        t0 = time()
        w, p, n = attack_rule(kind)
        println(rpad(string(kind), 7), lpad(round(w, digits = 6), 10), lpad(n, 4),
                lpad(round(w / C_TARGET, digits = 3), 8), lpad(round(w / 1.25, digits = 3), 8),
                lpad(round(rr(px, kind), digits = 5), 8), lpad(round(rr(py, kind), digits = 5), 8),
                lpad(round(rr(pz, kind), digits = 5), 8), lpad(round(rr(low, kind), digits = 5), 10))
        println("        见证 p = ", round.(p, digits = 4), "   (", round(time() - t0, digits = 0), "s)")
    end
    println("\npx = best-fit 的反例；py = 槽+LPT 的反例；pz = H2 的反例；“下界家族” = (1,1,1,r,r,r,s,s,s)")
    println("×c 越接近 1 越好（1.0 = 达到下界）；×5/4 < 1 才优于已知最优上界。")
end
main()
