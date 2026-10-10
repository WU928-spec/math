# a4_lib.jl —— m=4 候选算法族（经验评估用）
#
# 模板 A4(ρ, coords, slot, branch)：
#   开局：p1..p4 各占一台
#   安全线 τ = ρ · Λ，其中 Λ = max(coords 中各项)：
#        :p1        → p1                       （C* 下界：最大件单件）
#        :p45       → p4+p5                    （C* 下界：前 5 件塞 4 台必有两件同机）
#        :p56       → p5+p6                    （LP 验证为 C* 下界）
#        :min56_345 → min{p5+p6, p3+p4+p5}     （LP 验证为 C* 下界）
#        :p789      → p7+p8+p9（n>=9 时）       （LP 验证为 C* 下界）
#   每件 j>=5：①(slot) 若 M1 只含 p1 且 p1+pj <= τ → 入 M1（仅一次）
#             ②否则 E={M: ℓ(M)+pj <= τ}，取 E 中负载最大者
#             ③E 空 → 取负载最小者
#   branch=true：先判 p1+p5 <= ρ·(p1 与 p45 的 max)：
#        成立 → p5 入 M1（"顺利分支"），安全线沿用 τ
#        否则 → 安全线改用 ρ·Λ'（Λ' = max(coords ∪ {:min56_345})），p5 按 ②③ 放
include("common.jl")

struct A4
    rho::Float64
    coords::Vector{Symbol}
    slot::Bool
    branch::Bool
end
A4(rho, c::Symbol, slot, br) = A4(rho, [c], slot, br)

function coord_value(p::Vector{Float64}, names::Vector{Symbol})
    v = 0.0
    for s in names
        if s == :p1
            v = max(v, p[1])
        elseif s == :p45
            v = max(v, p[4] + p[5])
        elseif s == :p56
            length(p) >= 6 && (v = max(v, p[5] + p[6]))
        elseif s == :min56_345
            length(p) >= 6 && (v = max(v, min(p[5] + p[6], p[3] + p[4] + p[5])))
        elseif s == :p789
            length(p) >= 9 && (v = max(v, p[7] + p[8] + p[9]))
        end
    end
    return v
end

function a4_sim(p::Vector{Float64}, a::A4)
    n = length(p); load = zeros(4); cnt = zeros(Int, 4); asg = [Int[] for _ in 1:4]
    put(j, m) = (load[m] += p[j]; cnt[m] += 1; push!(asg[m], j))
    for j in 1:min(4, n); put(j, j); end
    n <= 4 && return (maximum(load), asg, load)

    Λ  = coord_value(p, a.coords)
    Λb = coord_value(p, a.coords ∪ [:min56_345])
    τ  = a.rho * Λ
    start = 5
    if a.branch
        if p[1] + p[5] <= a.rho * max(coord_value(p, [:p1]), coord_value(p, [:p45]))
            put(5, 1)                       # 顺利分支：p5 入 M1
        else
            τ = a.rho * Λb                  # 紧分支：安全线收紧
            E = [m for m in 1:4 if load[m] + p[5] <= τ]
            put(5, isempty(E) ? argmin(load) : E[argmax(load[E])])
        end
        start = 6
    end
    for j in start:n
        if a.slot && cnt[1] == 1 && p[1] + p[j] <= τ
            put(j, 1)
        else
            E = [m for m in 1:4 if load[m] + p[j] <= τ]
            put(j, isempty(E) ? argmin(load) : E[argmax(load[E])])
        end
    end
    return (maximum(load), asg, load)
end

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
            load[j] in tried && continue
            push!(tried, load[j])
            load[j] += p[i]; dfs(i + 1); load[j] -= p[i]
        end
    end
    dfs(1)
    return best[]
end

ratio(p, a) = a4_sim(p, a)[1] / opt_makespan(p, 4)

# ---------------------------------------------------------------- 实例家族
function gen_instance(n, rng; lower = ALPHA + 1e-9, family = :pow)
    p = Float64[]
    if family == :pow
        e = rand(rng, 1:3)
        p = [lower + rand(rng)^e * (1 - lower) for _ in 1:n]
    elseif family == :general
        p = [rand(rng) for _ in 1:n]
    elseif family == :blocks
        k = rand(rng, 2:4); vals = sort(rand(rng, k); rev = true)
        for v in vals
            append!(p, fill(lower + v * (1 - lower), rand(rng, 1:n)))
        end
        while length(p) < n; push!(p, lower + rand(rng) * (1 - lower)); end
        p = p[1:n]
    elseif family == :two
        a = lower + rand(rng) * (1 - lower); b = a * rand(rng)
        k = rand(rng, 1:n)
        p = vcat(fill(a, k), fill(max(b, lower), n - k))
    else                                    # :tight 围绕已知最坏形状扰动
        r = (2 + sqrt(37)) / 11; s = (13 + sqrt(37)) / 33
        p = [x * (1 + 0.15 * (rand(rng) - 0.5)) for x in vcat(fill(1.0, 3), fill(r, 3), fill(s, 3))]
        while length(p) < n; push!(p, lower + rand(rng) * 0.3); end
        p = p[1:n]
    end
    sort!(p; rev = true)
    return p
end

# ---------------------------------------------------------------- 攻击（定向爬山）
function attack(a::A4; nset = 8:12, restarts = 40, rounds = 250, seed = 2026)
    rng = MersenneTwister(seed)
    best = 0.0; bp = Float64[]; bn = 0
    for _ in 1:restarts
        n = rand(rng, nset)
        p = gen_instance(n, rng; family = rand(rng, (:pow, :blocks, :two, :tight, :general)),
                         lower = rand(rng) < 0.7 ? ALPHA + 1e-9 : 0.0)
        cur = ratio(p, a)
        for _ in 1:rounds
            improved = false
            for i in eachindex(p)
                for ε in (-0.25, -0.12, -0.05, -0.02, 0.02, 0.05, 0.12, 0.25, 0.6)
                    q = copy(p); q[i] = max(q[i] * (1 + ε), 0.0); sort!(q; rev = true)
                    r = ratio(q, a)
                    if r > cur + 1e-10; cur = r; p = q; improved = true; end
                end
            end
            for i in 1:length(p)
                for ε in (-0.2, -0.08, 0.08, 0.2)
                    q = copy(p); q[i:end] .*= (1 + ε); sort!(q; rev = true)
                    r = ratio(q, a)
                    if r > cur + 1e-10; cur = r; p = q; improved = true; end
                end
            end
            improved || break
        end
        cur > best && (best = cur; bp = copy(p); bn = length(p))
    end
    return best, bp, bn
end
