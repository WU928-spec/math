include("a4_lib.jl")

# 混合判据 H：动态闸门 = c · max{L_鸽笼, 已见工件总和/4}
#   每件 j>=5：若存在机器使 ℓ+pj <= τj  →  取其中**负载最大**者（"填"）
#              否则                      →  取**最轻**机（"平衡"）
function a4_hybrid(p::Vector{Float64}, rho = C_TARGET; use_avg = true)
    n = length(p); load = zeros(4); asg = [Int[] for _ in 1:4]
    put(j, m) = (load[m] += p[j]; push!(asg[m], j))
    for j in 1:min(4, n); put(j, j); end
    n <= 4 && return maximum(load)
    Λp = max(p[1], p[4] + p[5])
    seen = sum(p[1:4])
    for j in 5:n
        seen += p[j]
        # 有效 cap 取较小者：c·Λ_鸽笼 与 c·(已见总和/4)（两者都 <= c·C*）
        τ = use_avg ? min(rho * Λp, rho * (seen / 4)) : rho * Λp
        E = [m for m in 1:4 if load[m] + p[j] <= τ]
        put(j, isempty(E) ? argmin(load) : E[argmax(load[E])])
    end
    return maximum(load)
end
rh(p, rho = C_TARGET; use_avg = true) = a4_hybrid(p, rho; use_avg = use_avg) / opt_makespan(p, 4)

function attack_h(; rho = C_TARGET, use_avg = true, nset = 8:12, restarts = 40, rounds = 250, seed = 2026)
    rng = MersenneTwister(seed); best = 0.0; bp = Float64[]; bn = 0
    for _ in 1:restarts
        n = rand(rng, nset)
        p = gen_instance(n, rng; family = rand(rng, (:pow, :blocks, :two, :tight, :general)),
                         lower = rand(rng) < 0.7 ? ALPHA + 1e-9 : 0.0)
        cur = rh(p, rho; use_avg = use_avg)
        for _ in 1:rounds
            imp = false
            for i in eachindex(p)
                for ε in (-0.25, -0.12, -0.05, -0.02, 0.02, 0.05, 0.12, 0.25, 0.6)
                    q = copy(p); q[i] = max(q[i] * (1 + ε), 0.0); sort!(q; rev = true)
                    r = rh(q, rho; use_avg = use_avg)
                    r > cur + 1e-10 && (cur = r; p = q; imp = true)
                end
            end
            for i in 1:length(p)
                for ε in (-0.2, -0.08, 0.08, 0.2)
                    q = copy(p); q[i:end] .*= (1 + ε); sort!(q; rev = true)
                    r = rh(q, rho; use_avg = use_avg)
                    r > cur + 1e-10 && (cur = r; p = q; imp = true)
                end
            end
            imp || break
        end
        cur > best && (best = cur; bp = copy(p); bn = length(p))
    end
    return best, bp, bn
end

px  = [0.8694, 0.7341, 0.7203, 0.5947, 0.5883, 0.5871, 0.4412, 0.4288, 0.4273, 0.4267]  # best-fit 的反例
py  = [1.0862, 0.9842, 0.9527, 0.7885, 0.7548, 0.6149, 0.6068, 0.5735, 0.5598]          # 槽+LPT 的反例
rr = (2+sqrt(37))/11; ss = (13+sqrt(37))/33
low = vcat(fill(1.0,3), fill(rr,3), fill(ss,3))
println("混合 H2（闸门取两者较小者）：")
println("  best-fit 的反例上 = ", round(rh(px), digits = 5), "（c=", round(C_TARGET, digits=5), "）")
println("  槽+LPT 的反例上   = ", round(rh(py), digits = 5))
println("  下界家族上        = ", round(rh(low), digits = 5), "（应为 c）")
w1 = attack_h(use_avg = true)[1];  w2 = attack_h(use_avg = false)[1]
println("  攻击最坏（含均值）= ", round(w1, digits = 6), "   ", (w1 <= C_TARGET + 1e-9 ? "✓ 未破 c" : "✗ 破 c"))
println("  攻击最坏（无均值）= ", round(w2, digits = 6), "   ", (w2 <= C_TARGET + 1e-9 ? "✓ 未破 c" : "✗ 破 c"))
w, p, n = attack_h(use_avg = true)
println("  含均值版的攻击见证：n=", n, " p=", round.(p, digits = 4))
