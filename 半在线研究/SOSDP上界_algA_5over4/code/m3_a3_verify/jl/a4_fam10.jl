# a4_fam10.jl —— 卡点情形（n=10, Λ=p45, p2<p3+p4, p3<p45, p5<p3）的"轨迹空间"枚举
#
#   mode = sample  : 大样本采样，数一数该家族里到底有多少条不同的片（轨迹）
#   mode = dfs     : 在"松弛可行性 LP"（不含装箱）下做完全 DFS，枚举全部可行轨迹
#   mode = ceil    : 对给定片清单逐片求精确天花板（含装箱枚举）
#
# 用法：julia --project=. a4_fam10.jl sample 200000
#       julia --project=. a4_fam10.jl dfs 30000
include("a4_lib.jl")
include("a4_milp10.jl")
using JuMP, HiGHS, Random

const RHO = C_TARGET
const ALP = 4.0 / 15.0
const NT  = 10                    # 家族固定 n = 10

# ---------------------------------------------------------------- 轨迹
function trace10(p::Vector{Float64}, rho::Float64 = RHO)
    load = zeros(4); a = zeros(Int, NT); E = [Int[] for _ in 1:NT]
    for j in 1:4; a[j] = j; load[j] += p[j]; end
    τ = rho * (p[4] + p[5])
    for j in 5:NT
        Ej = [m for m in 1:4 if load[m] + p[j] <= τ + 1e-15]; E[j] = collect(Ej)
        a[j] = isempty(Ej) ? argmin(load) : Ej[argmax(load[Ej])]
        load[a[j]] += p[j]
    end
    return a, E, argmax(load)
end

piecekey(a, E, am) = string(join(a[5:10], "-"), "|", join([join(sort(E[j]), "") for j in 5:10], "-"), "|", am)

in_family(p) = (p[4] + p[5] >= p[1] - 1e-12) && (p[2] <= p[3] + p[4] + 1e-12) &&
               (p[3] <= p[4] + p[5] + 1e-12) && (p[5] <= p[3] + 1e-12) &&
               (minimum(p) >= ALP - 1e-9)

# ---------------------------------------------------------------- 采样
function sample(N::Int, seed::Int)
    rng = MersenneTwister(seed); seen = Dict{String,Int}(); nf = 0; ntot = 0
    bestr = 0.0; bestp = Float64[]
    a4 = A4(C_TARGET, [:p1, :p45], false, false)
    while ntot < N
        ntot += 1
        n = 10
        p = rand(rng) < 0.5 ? sort(Float64[rand(rng, 1:20) / 20 for _ in 1:n]; rev = true) :
                              sort(Float64[ALP + rand(rng)^2 * (1 - ALP) for _ in 1:n]; rev = true)
        cs = opt_makespan(p, 4); pn = p ./ cs
        minimum(pn) < ALP - 1e-12 && continue
        in_family(pn) || continue
        nf += 1
        k = piecekey(trace10(pn)...); seen[k] = get(seen, k, 0) + 1
        r = a4_sim(pn, a4)[1]
        if r > bestr; bestr = r; bestp = copy(pn); end
    end
    println("采样实例 ", ntot, "，落在家族内 ", nf, "，不同片数 ", length(seen))
    println("家族内 A4c 最大比值 = ", round(bestr, digits = 8), "  实例 ", round.(bestp, digits = 4))
    ks = sort(collect(seen); by = x -> -x[2])
    for (k, c) in ks[1:min(20, end)]; println("   ", rpad(k, 32), c); end
    return seen
end

# ---------------------------------------------------------------- 松弛可行性 LP（无装箱）
struct Con; coef::Vector{Tuple{Int,Float64}}; op::Symbol; rhs::Float64; end
le(c, r) = Con(c, :le, r)
ge(c, r) = Con(c, :ge, r)

function fam_cons()
    c = Con[]
    for i in 1:(NT-1); push!(c, le([(i, 1.0), (i + 1, -1.0)], 0.0)); end   # p_i >= p_{i+1}
    push!(c, ge([(NT, 1.0)], ALP))
    push!(c, le([(1, 1.0)], 1.0))                                          # 归一化 C*=1 ⟹ p1<=1
    push!(c, ge([(4, 1.0), (5, 1.0), (1, -1.0)], 0.0))                     # p4+p5 >= p1
    push!(c, le([(2, 1.0), (3, -1.0), (4, -1.0)], 0.0))                    # p2 <= p3+p4
    push!(c, le([(3, 1.0), (4, -1.0), (5, -1.0)], 0.0))                    # p3 <= p4+p5
    push!(c, le([(5, 1.0), (3, -1.0)], 0.0))                               # p5 <= p3
    # 下面是"可装箱"的必要条件（便宜且强）：任何 C*=1 的点都满足，故不会误剪
    push!(c, le([(i, 1.0) for i in 1:NT], 4.0))                            # 总容量 4
    push!(c, le([(5, 1.0)], 0.5))                                          # >1/2 的件至多 4 个
    push!(c, le([(9, 1.0)], 1.0 / 3.0))                                    # >1/3 的件至多 8 个
    return c
end

# 把约束列表喂给 HiGHS，只判可行性。轨迹/家族约束都是齐次的，
# 所以用"缩放变量 s"代替固定下界，保证松弛是真正的超集（不会误剪）。
function feasible(cons::Vector{Con}, s::Float64 = ALP)
    m = Model(HiGHS.Optimizer); set_silent(m)
    @variable(m, p[1:NT]); for i in 1:NT; set_lower_bound(p[i], 0.0); end
    @variable(m, sc); set_lower_bound(sc, 0.0); set_upper_bound(sc, 1.0)
    for i in 1:NT; @constraint(m, p[i] >= s * sc); end
    for c in cons
        e = sum(k * p[i] for (i, k) in c.coef; init = 0.0 * p[1])
        c.op == :le ? @constraint(m, e <= c.rhs) : @constraint(m, e >= c.rhs)
    end
    optimize!(m)
    return termination_status(m) == OPTIMAL
end

"给出第 j 步（把 p_j 放到 a_j、可集为 E_j）的线性约束"
function step_cons(j::Int, Ej::Vector{Int}, aj::Int, prior::Vector{Int})
    # ℓ_m = p_m + Σ_{5<=i<j, a_i=m} p_i ；τ = ρ(p4+p5)
    ℓ = [Vector{Tuple{Int,Float64}}([(m, 1.0)]) for m in 1:4]
    for i in 5:(j-1); push!(ℓ[prior[i-4]], (i, 1.0)); end
    τc = [(4, RHO), (5, RHO)]
    minus(a, b) = vcat([(i, k) for (i, k) in a], [(i, -k) for (i, k) in b])
    out = Con[]
    for m in 1:4
        row = vcat(ℓ[m], [(j, 1.0)])
        if m in Ej; push!(out, le(minus(row, τc), 0.0))     # ℓ_m + p_j <= τ
        else;       push!(out, ge(minus(row, τc), 0.0)); end # ℓ_m + p_j >= τ
    end
    if isempty(Ej)
        for m in 1:4; m == aj && continue; push!(out, le(minus(ℓ[aj], ℓ[m]), 0.0)); end  # aj = argmin
    else
        for m in Ej; m == aj && continue; push!(out, ge(minus(ℓ[aj], ℓ[m]), 0.0)); end   # aj = argmax on E
    end
    return out
end

function dfs(budget::Int)
    fam = fam_cons(); leaves = Dict{String,Vector{Any}}(); nodes = Ref(0); hitbudget = Ref(false)
    function rec(j::Int, steps::Vector{Any}, acc::Vector{Con})
        nodes[] += 1
        if nodes[] > budget; hitbudget[] = true; return; end
        if j > NT
            leaves[string(join([(s[2], join(sort(s[1]), "")) for s in steps], "/"))] = copy(steps)
            return
        end
        for mask in 0:15
            Ej = [m for m in 1:4 if (mask >> (m - 1)) & 1 == 1]
            for aj in (isempty(Ej) ? (1:4) : Ej)
                cons = vcat(acc, step_cons(j, Ej, aj, Int[s[2]::Int for s in steps]))
                feasible(vcat(fam, cons)) || continue
                rec(j + 1, vcat(steps, Any[(Ej, aj)]), cons)
            end
        end
    end
    rec(5, Any[], Con[])
    println("DFS 节点 ", nodes[], "  叶子(轨迹) ", length(leaves), hitbudget[] ? "  [预算用尽]" : "  [完全]")
    open("fam10_leaves.txt", "w") do io
        for (k, steps) in leaves
            ks = [Int[s[2]::Int for s in steps]...]
            ms = [sum(1 << (m - 1) for m in s[1]::Vector{Int}; init = 0) for s in steps]
            println(io, join(vcat(ks, ms), "\t"))
        end
    end
    println("叶子已写入 fam10_leaves.txt（12 列：a5..a10 与 E5..E10 的位掩码）")
    return leaves
end

function dfs2(budget::Int, si::Int = 0, sk::Int = 1)
    leaves = Dict{String,Vector{Any}}(); nodes = Ref(0); hitbudget = Ref(false); nprune = Ref(0)
    function rootopts()
        o = Vector{Tuple{Vector{Int},Int}}()
        for mask in 0:15
            Ej = [m for m in 1:4 if (mask >> (m - 1)) & 1 == 1]
            for aj in (isempty(Ej) ? (1:4) : Ej)
                push!(o, (Ej, aj))
            end
        end
        return o
    end
    function rec(j::Int, steps::Vector{Any})
        nodes[] += 1
        nodes[] % 200 == 0 && (println("  [进度] 节点 ", nodes[], "  剪枝 ", nprune[], "  叶子 ", length(leaves)); flush(stdout))
        if nodes[] > budget; hitbudget[] = true; return; end
        if j > NT
            leaves[string(join([(s[2], join(sort(s[1]), "")) for s in steps], "/"))] = copy(steps)
            return
        end
        kp = Int[s[2]::Int for s in steps]
        mp = [sum(1 << (m - 1) for m in (s[1]::Vector{Int}); init = 0) for s in steps]
        opts = j == 5 ? [o for (idx, o) in enumerate(rootopts()) if (idx - 1) % sk == si] : rootopts()
        for (Ej, aj) in opts
            piece_feasible(vcat(kp, aj), vcat(mp, (isempty(Ej) ? 0 : sum(1 << (m - 1) for m in Ej; init = 0)))) ||
                (nprune[] += 1; continue)
            rec(j + 1, vcat(steps, Any[(Ej, aj)]))
            hitbudget[] && return
        end
    end
    rec(5, Any[])
    println("DFS2 节点 ", nodes[], "  剪枝 ", nprune[], "  叶子(片) ", length(leaves),
            hitbudget[] ? "  [预算用尽]" : "  [完全]")
    open("fam10_leaves2_$(si).txt", "w") do io
        for (_, steps) in leaves
            ks = Int[s[2]::Int for s in steps]
            ms = [sum(1 << (m - 1) for m in s[1]::Vector{Int}; init = 0) for s in steps]
            println(io, join(vcat(ks, ms), "\t"))
        end
    end
    println("叶子已写入 fam10_leaves2_$(si).txt")
    return leaves
end

function main()
    mode = ARGS[1]
    if mode == "sample"
        sample(parse(Int, ARGS[2]), length(ARGS) >= 3 ? parse(Int, ARGS[3]) : 1)
    elseif mode == "dfs"
        dfs(parse(Int, ARGS[2]))
    elseif mode == "dfs2"
        dfs2(parse(Int, ARGS[2]), length(ARGS) >= 4 ? parse(Int, ARGS[3]) : 0,
             length(ARGS) >= 4 ? parse(Int, ARGS[4]) : 1)
    end
end
main()
