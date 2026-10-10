# common.jl —— m=3 / m=4 验证公共库（Julia + JuMP + HiGHS）
# 用途：复现《CKK2012 m=3 最优上界 A3 完整证明》文档 §6 / 附录 B 的全部 LP 与随机验证，
#       并提供 m=4 候选"值坐标"的筛选器。
using JuMP, HiGHS
using Random

const C_TARGET = (1 + sqrt(37)) / 6      # c = 1.180460421716370
const ALPHA    = 1.5 * (C_TARGET - 1)    # (3/2)(c-1) = 0.270690632574555（O3 的工件下界）

# ---------------------------------------------------------------- 装箱结构枚举
"""规范枚举：把 1:n 分成 <=nblocks 个非空块、每块 <=maxb 个元素。
（总是取最小剩余元素：或加入已有块，或新开一块 ⟹ 每个集合划分恰好生成一次）"""
function partitions(n::Int, maxb::Int, nblocks::Int)
    out = Vector{Vector{Vector{Int}}}()
    blocks = Vector{Vector{Int}}()
    function rec(rest::Vector{Int})
        if isempty(rest)
            push!(out, [copy(b) for b in blocks]); return
        end
        e = first(rest)
        for i in eachindex(blocks)
            if length(blocks[i]) < maxb
                push!(blocks[i], e); rec(rest[2:end]); pop!(blocks[i])
            end
        end
        if length(blocks) < nblocks
            push!(blocks, [e]); rec(rest[2:end]); pop!(blocks)
        end
    end
    rec(collect(1:n))
    return out
end

# ---------------------------------------------------------------- LP 求解
const Row = Vector{Tuple{Int,Float64}}          # 线性式：(下标, 系数) 列表

"把 (i,coef) 列表拼成 JuMP 表达式"
function expr(p, row::Row)
    return sum(coef * p[i] for (i, coef) in row; init = 0.0 * p[1])
end

"""在每个装箱结构上求各目标的最大值。
objectives[o] 是一组线性式，目标 o = 最大化这组式的 **min**（单个式即直接最大化它）。
额外变量 t[o] 满足 t[o] <= 该组每个式 ⟹ max t[o] = max min(式)。
extra 为附加线性约束 (row, 上界)（用于分支测试）。返回 [(最大值, 见证 p), ...]。"""
function solve_lp(; n::Int, parts, objectives::Vector{Vector{Row}},
                  low::Float64 = ALPHA, extra::Vector{Tuple{Row,Float64}} = Tuple{Row,Float64}[])
    nobj = length(objectives)
    best = [(-Inf, Float64[]) for _ in 1:nobj]
    for blocks in parts
        model = Model(HiGHS.Optimizer); set_silent(model)
        @variable(model, p[1:n])
        @variable(model, t[1:nobj])
        for i in 1:n
            set_lower_bound(p[i], low)
        end
        for blk in blocks
            @constraint(model, sum(p[i] for i in blk) <= 1.0)
        end
        for i in 1:(n-1)                        # p_1 >= p_2 >= ... >= p_n
            @constraint(model, p[i] >= p[i+1])
        end
        for (row, b) in extra
            @constraint(model, expr(p, row) <= b)
        end
        for oi in 1:nobj
            for r in objectives[oi]
                @constraint(model, t[oi] <= expr(p, r))     # t[oi] <= 每个式
            end
        end
        for oi in 1:nobj
            @objective(model, Max, t[oi])
            optimize!(model)
            if termination_status(model) == OPTIMAL
                v = objective_value(model)
                if v > best[oi][1] + 1e-12
                    best[oi] = (v, value.(p))
                end
            end
        end
    end
    return best
end

# ---------------------------------------------------------------- A3 模拟与暴力最优
"""A3（m=3）逐件模拟。返回 (makespan, 每台机器上的工件下标, 负载)。"""
function a3_sim(p::Vector{Float64})
    n = length(p); load = zeros(3); asg = [Int[] for _ in 1:3]
    put(j, m) = (load[m] += p[j]; push!(asg[m], j))
    put(1, 1); n >= 2 && put(2, 2); n >= 3 && put(3, 3)
    n <= 3 && return (maximum(load), asg, load)
    L0 = max(p[1], p[3] + p[4])
    if p[1] + p[4] <= C_TARGET * L0
        put(4, 1)
        if n > 4
            put(5, 2)
            for j in 6:n
                m = argmin(load); put(j, m)
            end
        end
    else
        put(4, 3)
        if n > 4
            L = max(L0, min(p[2] + p[5], p[3] + p[4] + p[5]))
            for j in 5:n
                if length(asg[1]) == 1 && p[1] + p[j] <= C_TARGET * L
                    put(j, 1)
                else
                    m = argmin(load); put(j, m)
                end
            end
        end
    end
    return (maximum(load), asg, load)
end

"""暴力最优（m 台机器，n 件，枚举 m^n 种指派）。"""
function brute_opt(p::Vector{Float64}, m::Int = 3)
    n = length(p); best = Inf; load = zeros(m)
    idx = zeros(Int, n)
    total = m^n
    for code in 0:(total-1)
        fill!(load, 0.0); c = code
        for j in 1:n
            idx[j] = c % m + 1; c ÷= m
            load[idx[j]] += p[j]
        end
        mx = maximum(load)
        mx < best && (best = mx)
    end
    return best
end

"随机非增实例：所有工件 > ALPHA，并按需归一化使 C* <= 1"
function rand_instance(n::Int, rng; alpha::Float64 = ALPHA + 1e-9, normalize::Bool = true)
    p = Float64[]
    for _ in 1:n
        push!(p, max(rand(rng)^rand(rng, 1:3), alpha))   # 幂律形状，下界 alpha
    end
    sort!(p; rev = true)
    if normalize
        ov = brute_opt(p, 3)
        ov > 1 && (p ./= ov)
    end
    return p
end

# ---------------------------------------------------------------- 小工具
"构造线性式：term((i,coef), ...)"
term(args::Vararg{Tuple{Int,Float64}}) = collect(args)
"打印一行结果"
function report(name, val, target = nothing)
    ok = target === nothing ? "" : (val <= target + 1e-9 ? "  ✓ <= $target" : "  ✗ > $target")
    println(rpad(name, 30), lpad(round(val, digits = 6), 12), ok)
end
