include("a4_lib.jl")

# A3 式机制（注意：A3 里 **没有 best-fit**！）：cap 门控的"专用槽" + 最轻机兜底
#  S1：开局 p1..p4 各一台；τ = c·max{p1,p4+p5}；j>=5：若 M1 只含 p1 且 p1+pj <= τ → M1；否则 → 最轻机
#  S2：同上，但槽改为"任一目前只有 1 件、且放上去 <= τ 的机器里负载最小者"（更对称）
#  S3：双分支：p1+p5 <= c·L0 时 p5→M1（顺利分支，此后同样走槽/LPT）；
#             否则先按普通规则放 p5，安全线改用 c·max{L0, min{p5+p6, p3+p4+p5}}。
function a4_slot(p::Vector{Float64}, kind::Symbol, rho = C_TARGET)
    n = length(p); load = zeros(4); cnt = zeros(Int, 4); asg = [Int[] for _ in 1:4]
    put(j, m) = (load[m] += p[j]; cnt[m] += 1; push!(asg[m], j))
    for j in 1:min(4, n); put(j, j); end
    n <= 4 && return maximum(load)
    L0 = max(p[1], p[4] + p[5])
    Λ  = kind == :S3 ? max(L0, min(p[5] + p[6], p[3] + p[4] + p[5])) : L0
    τ  = rho * Λ
    start = 5
    if kind == :S3 && p[1] + p[5] <= rho * L0
        put(5, 1); start = 6                     # 顺利分支：p5 入 M1
    end
    for j in start:n
        if kind == :S2
            E = [m for m in 1:4 if cnt[m] == 1 && load[m] + p[j] <= τ]
            if !isempty(E); put(j, E[argmin(load[E])]); continue; end
        else
            if cnt[1] == 1 && p[1] + p[j] <= τ; put(j, 1); continue; end
        end
        put(j, argmin(load))                      # 兜底：最轻机（LPT），**不做 best-fit**
    end
    return maximum(load)
end
rslot(p, kind; rho = C_TARGET) = a4_slot(p, kind, rho) / opt_makespan(p, 4)

function attack_slot(kind::Symbol; rho = C_TARGET, nset = 8:12, restarts = 40, rounds = 250, seed = 2026)
    rng = MersenneTwister(seed); best = 0.0; bp = Float64[]; bn = 0
    for _ in 1:restarts
        n = rand(rng, nset)
        p = gen_instance(n, rng; family = rand(rng, (:pow, :blocks, :two, :tight, :general)),
                         lower = rand(rng) < 0.7 ? ALPHA + 1e-9 : 0.0)
        cur = rslot(p, kind; rho = rho)
        for _ in 1:rounds
            imp = false
            for i in eachindex(p)
                for ε in (-0.25, -0.12, -0.05, -0.02, 0.02, 0.05, 0.12, 0.25, 0.6)
                    q = copy(p); q[i] = max(q[i] * (1 + ε), 0.0); sort!(q; rev = true)
                    r = rslot(q, kind; rho = rho)
                    r > cur + 1e-10 && (cur = r; p = q; imp = true)
                end
            end
            for i in 1:length(p)
                for ε in (-0.2, -0.08, 0.08, 0.2)
                    q = copy(p); q[i:end] .*= (1 + ε); sort!(q; rev = true)
                    r = rslot(q, kind; rho = rho)
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
rr = (2 + sqrt(37)) / 11; ss = (13 + sqrt(37)) / 33
low = vcat(fill(1.0, 3), fill(rr, 3), fill(ss, 3))
println("诊断实例：S1=", round(rslot(px, :S1), digits = 5), "  S2=", round(rslot(px, :S2), digits = 5),
        "  S3=", round(rslot(px, :S3), digits = 5), "   (c=", round(C_TARGET, digits = 5), ", LPT=1.10518)")
println("下界家族：S1=", round(rslot(low, :S1), digits = 5), "  S2=", round(rslot(low, :S2), digits = 5),
        "  S3=", round(rslot(low, :S3), digits = 5))
println("-"^84)
for kind in (:S1, :S2, :S3)
    w, p, n = attack_slot(kind)
    println(rpad(string(kind), 5), " 攻击最坏比值 = ", rpad(round(w, digits = 6), 10), " n=", lpad(n, 2),
            "   ", (w <= C_TARGET + 1e-9 ? "✓ 未破 c" : "✗ 破 c"))
    println("      p = ", round.(p, digits = 4))
end
