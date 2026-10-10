# a4_search.jl —— m=4 候选算法搜索（经验评估，无证明）
#
# 模板族 A4(ρ, coord, slot, branch)：
#   开局：p1..p4 各占一台
#   坐标：coord = :p45   → Λ = p4+p5            （= Algorithm A 在 m=4 的 L）
#                = :L0   → Λ = max{p1, p4+p5}    （已验证为 C* 下界）
#                = :L1   → Λ = max{L0, min{p5+p6, p3+p4+p5}}（已验证为 C* 下界）
#   安全线：τ = ρ·Λ
#   每件 j>=5：①（slot=true 时）若 M1 只含 p1 且 p1+pj <= τ → 入 M1（仅一次）
#             ②否则 E={M: ℓ(M)+pj <= τ}，取 E 中负载最大者
#             ③E 空 → 取负载最小者
#   branch=true 时：先看 p1+p5 <= ρ·L0 是否成立；成立则 p5 入 M1（"顺利分支"），
#                   否则 p5 走 ②/③ 且全体改用坐标 L1。
include("common.jl")

# ---------------------------------------------------------------- 精确最优（分支定界）
function opt_makespan(p::Vector{Float64}, m::Int = 4)
    n = length(p); load = zeros(m); best = Ref(Inf)
    function dfs(i::Int)
        if i > n
            mx = maximum(load); mx < best[] && (best[] = mx); return
        end
        maximum(load) >= best[] && return
        tried = Float64[]
        for j in 1:m
            load[j] in tried && continue                    # 对称剪枝
            push!(tried, load[j])
            load[j] += p[i]; dfs(i + 1); load[j] -= p[i]
        end
    end
    dfs(1)
    return best[]
end

# ---------------------------------------------------------------- A4 模拟
struct A4
    rho::Float64
    coord::Symbol          # :p45 | :L0 | :L1
    slot::Bool
    branch::Bool
end

function a4_sim(p::Vector{Float64}, a::A4)
    n = length(p); load = zeros(4); cnt = zeros(Int, 4); asg = [Int[] for _ in 1:4]
    put(j, m) = (load[m] += p[j]; cnt[m] += 1; push!(asg[m], j))
    for j in 1:min(4, n); put(j, j); end
    n <= 4 && return (maximum(load), asg, load)

    L0 = max(p[1], p[4] + p[5])
    L1 = n >= 6 ? max(L0, min(p[5] + p[6], p[3] + p[4] + p[5])) : L0
    name(x) = x == :p45 ? p[4] + p[5] : x == :L0 ? L0 : L1
    start = 5
    tau = a.rho * name(a.coord)
    if a.branch
        if p[1] + p[5] <= a.rho * L0
            put(5, 1); tau = a.rho * L0            # 顺利分支：p5 入 M1，此后用 L0 的线
        else
            tau = a.rho * L1                        # 紧分支：改用 L1
        end
        start = 6
    end
    for j in start:n
        if a.slot && cnt[1] == 1 && p[1] + p[j] <= tau
            put(j, 1)
        else
            E = [m for m in 1:4 if load[m] + p[j] <= tau]
            put(j, isempty(E) ? argmin(load) : E[argmax(load[E])])
        end
    end
    return (maximum(load), asg, load)
end

ratio(p, a) = a4_sim(p, a)[1] / opt_makespan(p, 4)

# ---------------------------------------------------------------- 实例家族
"n 件非增实例；lower = 工件下界（0 表示无下界）"
function gen_instance(n, rng; lower = ALPHA + 1e-9, family = :pow)
    p = Float64[]
    if family == :pow
        e = rand(rng, 1:3)
        p = [lower + rand(rng)^e * (1 - lower) for _ in 1:n]
    elseif family == :blocks                       # 等值块（下界构造的形状）
        k = rand(rng, 2:4); vals = sort(rand(rng, k); rev = true)
        p = Float64[]
        for v in vals
            c = rand(rng, 1:n); append!(p, fill(lower + v * (1 - lower), c))
        end
        p = p[1:min(length(p), n)]
        while length(p) < n; push!(p, lower + rand(rng) * (1 - lower)); end
    elseif family == :two                          # 两级：大若干 + 小若干
        a = lower + rand(rng) * (1 - lower); b = a * rand(rng)
        k = rand(rng, 1:n)
        p = vcat(fill(a, k), fill(max(b, lower), n - k))
    else                                           # :tight 围绕已知最坏形状扰动
        r = (2 + sqrt(37)) / 11; s = (13 + sqrt(37)) / 33
        base = vcat(fill(1.0, 3), fill(r, 3), fill(s, 3))
        p = [x * (1 + 0.15 * (rand(rng) - 0.5)) for x in base]
        while length(p) < n; push!(p, lower + rand(rng) * 0.3); end
        p = p[1:n]
    end
    sort!(p; rev = true)
    return p
end

"在若干家族 × 若干 n 上搜索某组参数的最坏比值（返回 最坏比值, 见证实例, n）"
function search_worst(a::A4; samples_per_cell = 1500, nrange = 5:12, seed = 1)
    rng = MersenneTwister(seed)
    worst = 0.0; wit = Float64[]
    for n in nrange, fam in (:pow, :blocks, :two, :tight)
        for _ in 1:samples_per_cell
            p = gen_instance(n, rng; family = fam)
            r = ratio(p, a)
            r > worst && (worst = r; wit = copy(p))
        end
    end
    # 局部搜索：围绕最坏实例做坐标扰动
    p = wit
    improved = true
    while improved && !isempty(p)
        improved = false
        for i in eachindex(p)
            for δ in (-0.05, -0.02, 0.02, 0.05)
                q = copy(p); q[i] = max(q[i] * (1 + δ), ALPHA + 1e-9)
                sort!(q; rev = true)
                r = ratio(q, a)
                if r > worst + 1e-9
                    worst = r; p = q; wit = copy(q); improved = true
                end
            end
        end
    end
    return worst, wit
end

# ---------------------------------------------------------------- 主扫描
function main()
    println("="^96)
    println("m=4 候选算法搜索（经验评估；opt 由分支定界精确求得）")
    println("="^96)
    # 先验证框架：coord=:p45, ρ=5/4, 无槽、无分支 ≈ Algorithm A（应复现 <= 5/4）
    grid = [
        A4(5/4, :p45, false, false),
        A4(5/4, :L0,  false, false),
        A4(C_TARGET, :p45, false, false),
        A4(C_TARGET, :L0,  false, false),
        A4(C_TARGET, :L1,  false, false),
        A4(C_TARGET, :L0,  true,  false),
        A4(C_TARGET, :L1,  true,  false),
        A4(C_TARGET, :L0,  true,  true),
        A4(1.22, :L1, true, false),
        A4(1.20, :L1, true, false),
        A4(1.19, :L1, true, true),
    ]
    println(rpad("ρ", 9), rpad("coord", 7), rpad("slot", 6), rpad("branch", 8),
            lpad("最坏比值", 11), "   见证实例（4dp）")
    println("-"^96)
    for a in grid
        w, p = search_worst(a; samples_per_cell = 150, seed = 7)
        flag = w <= C_TARGET + 1e-9 ? "  ✓ <= c" : (w <= 1.25 + 1e-9 ? "  <= 5/4" : "  ✗ > 5/4")
        println(rpad(string(round(a.rho, digits = 6)), 9), rpad(string(a.coord), 7),
                rpad(string(a.slot), 6), rpad(string(a.branch), 8),
                lpad(round(w, digits = 5), 11), flag)
        w > 1.15 && println("      见证 p = ", round.(p, digits = 4))
    end
    println("\n注：这是经验搜索的**下界方向**证据（找到的最坏实例）；比值 ≤ c 只表示搜索未找到反例，不构成证明。")
end

main()
