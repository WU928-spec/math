# a4_milp10.jl —— 单条片（n=10 家族）的精确 MILP：装箱 + 轨迹
#
#   变体：
#     milp_piece(heaviest=0)      只判可行性（DFS 预言机）
#     milp_piece(heaviest=m)      固定最重机求最大负载
#     milp_piece(heaviest=m, level=L)  判"能否把 m 压到 ≥L"（可行性）
#     milp_sel(level=L)           **单次求解**：用 4 个二元选最重机（比 4 次求解省）
#     milp_sel(level=Inf)         **单次求解**：直接给天花板
#     seq_milp(masks, level)      **固定 E 序列、放置自由**的合并松弛（一次覆盖该 E 序列的所有并列变体）
#
# preds = :card  → 卡点家族四条谓词；:full45 → 只要求 Λ=p45；:full1 → Λ=p1
include("common.jl")
using JuMP, HiGHS

const RHO = C_TARGET
const ALP = 4.0 / 15.0
const NT  = 10
const BIGM = 4.0                     # 单机负载 ≤ Σp ≤ 4

# 求解器可切换（交叉验证用）：默认 HiGHS；在驱动脚本里 OPTIMIZER[] = Cbc.Optimizer 即可换
const OPTIMIZER = Ref{Any}(HiGHS.Optimizer)

"装箱（C*<=1, ≤4 箱, 每箱 ≤3 件）+ 家族谓词；返回 (model, P)
  cuts=true 时加「冲突割」：若若干件之和 >1 就不可能同箱
    —— 成对：p_i+p_j ≥ 1 ⟹ x[i,b]+x[j,b] ≤ 1
    —— 三元：p_i+p_j+p_k ≥ 1 ⟹ x[i,b]+x[j,b]+x[k,b] ≤ 2
   这些都是可装箱性的**合法推论**（不改变精确可行集），只加强 LP 松弛，有利于「证不可行」。"
function _base(n::Int; preds::Symbol = :card, cuts::Bool = false)
    m = Model(OPTIMIZER[]); set_silent(m)
    @variable(m, P[1:n])
    for i in 1:n; set_lower_bound(P[i], ALP); set_upper_bound(P[i], 1.0); end
    for i in 1:(n-1); @constraint(m, P[i] >= P[i+1]); end
    if preds == :full1
        @constraint(m, P[1] >= P[4] + P[5])
    else
        @constraint(m, P[4] + P[5] >= P[1])
    end
    if preds == :card
        @constraint(m, P[2] <= P[3] + P[4])
        @constraint(m, P[3] <= P[4] + P[5])
        @constraint(m, P[5] <= P[3])
    end
    @constraint(m, sum(P) <= 4.0)
    @variable(m, x[1:n, 1:4], Bin)
    @variable(m, y[1:n, 1:4])
    for i in 1:n
        @constraint(m, sum(x[i, :]) == 1)
        for b in 1:4
            @constraint(m, y[i, b] <= x[i, b])
            @constraint(m, y[i, b] <= P[i])
            @constraint(m, y[i, b] >= P[i] - (1 - x[i, b]))
            @constraint(m, y[i, b] >= 0)
        end
    end
    for b in 1:4
        @constraint(m, sum(y[i, b] for i in 1:n) <= 1.0)
        @constraint(m, sum(x[i, b] for i in 1:n) <= 3)
    end
    @constraint(m, x[1, 1] == 1)
    if cuts
        for b in 1:4
            for i in 1:n, j in (i+1):n
                @constraint(m, x[i, b] + x[j, b] <= 1 + 3.0 * (1 - P[i] - P[j]))
            end
            for i in 1:n, j in (i+1):n, k in (j+1):n
                @constraint(m, x[i, b] + x[j, b] + x[k, b] <= 2 + 3.0 * (1 - P[i] - P[j] - P[k]))
            end
        end
    end
    return m, P
end

Eset(mask::Int) = [mm for mm in 1:4 if (mask >> (mm - 1)) & 1 == 1]

"轨迹约束（固定 a、固定 E）；返回最终负载表达式向量 ℓ"
function _trace!(m, P, k::Vector{Int}, masks::Vector{Int}; n::Int, preds::Symbol = :card)
    τ = preds == :full1 ? RHO * P[1] : RHO * (P[4] + P[5])
    ℓ = [AffExpr(0.0) for _ in 1:4]
    for mm in 1:4; ℓ[mm] += P[mm]; end
    for c in 1:length(k)
        j = 4 + c
        Ej = Eset(masks[c]); aj = k[c]
        pre = copy(ℓ)
        for mm in 1:4
            if mm in Ej; @constraint(m, pre[mm] + P[j] <= τ)
            else;        @constraint(m, pre[mm] + P[j] >= τ); end
        end
        if isempty(Ej)
            for mm in 1:4; @constraint(m, pre[aj] <= pre[mm]); end
        else
            for mm in Ej; @constraint(m, pre[aj] >= pre[mm]); end
        end
        ℓ[aj] += P[j]
    end
    return ℓ
end

"原版：heaviest=0 判可行性；heaviest=m 优化/判 level"
function milp_piece(k::Vector{Int}, masks::Vector{Int}; heaviest::Int = 0,
                    timelimit::Float64 = 300.0, level::Float64 = Inf, preds::Symbol = :card,
                    cuts::Bool = false)
    n = 4 + length(k)
    m, P = _base(n; preds = preds, cuts = cuts); set_time_limit_sec(m, timelimit)
    ℓ = _trace!(m, P, k, masks; n = n, preds = preds)
    if heaviest == 0
        set_objective_sense(m, MOI.FEASIBILITY_SENSE)
    elseif level < Inf
        @constraint(m, ℓ[heaviest] >= level)
        set_objective_sense(m, MOI.FEASIBILITY_SENSE)
    else
        for mm in 1:4; mm == heaviest && continue; @constraint(m, ℓ[heaviest] >= ℓ[mm]); end
        @objective(m, Max, ℓ[heaviest])
    end
    t0 = time(); optimize!(m); el = time() - t0
    st = termination_status(m)
    val = (st == OPTIMAL) ? (heaviest == 0 || level < Inf ? 0.0 : objective_value(m)) : NaN
    return val, el, st
end

# 单次求解：4 个二元选最重机。level<Inf 判「是否有 ℓ_m ≥ level」；否则直接给天花板
function milp_sel(k::Vector{Int}, masks::Vector{Int}; level::Float64 = Inf,
                  timelimit::Float64 = 300.0, preds::Symbol = :card, cuts::Bool = false)
    n = 4 + length(k)
    m, P = _base(n; preds = preds, cuts = cuts); set_time_limit_sec(m, timelimit)
    ℓ = _trace!(m, P, k, masks; n = n, preds = preds)
    @variable(m, z[1:4], Bin)
    @constraint(m, sum(z) == 1)
    if level < Inf
        for mm in 1:4; @constraint(m, ℓ[mm] >= level - BIGM * (1 - z[mm])); end
        set_objective_sense(m, MOI.FEASIBILITY_SENSE)
        t0 = time(); optimize!(m); el = time() - t0
        return 0.0, el, termination_status(m)
    else
        @variable(m, t)
        for mm in 1:4; @constraint(m, t <= ℓ[mm] + BIGM * (1 - z[mm])); end
        @objective(m, Max, t)
        t0 = time(); optimize!(m); el = time() - t0
        st = termination_status(m)
        return (st == OPTIMAL ? objective_value(m) : NaN), el, st
    end
end

"固定 E 序列、放置自由（合法超集，覆盖该 E 序列的全部并列变体）"
function seq_milp(masks::Vector{Int}; level::Float64 = Inf, timelimit::Float64 = 300.0,
                 preds::Symbol = :card)
    n = 4 + length(masks)
    m, P = _base(n; preds = preds); set_time_limit_sec(m, timelimit)
    τ = RHO * (P[4] + P[5])
    ℓ = [AffExpr(0.0) for _ in 1:4]
    for mm in 1:4; ℓ[mm] += P[mm]; end
    for c in 1:length(masks)
        j = 4 + c; Ej = Eset(masks[c])
        pre = copy(ℓ)
        allow = isempty(Ej) ? (1:4) : Ej
        @variable(m, w[1:4], Bin)
        @variable(m, q[1:4])
        for mm in 1:4
            if mm in allow
                @constraint(m, q[mm] <= P[j]); @constraint(m, q[mm] <= w[mm])
                @constraint(m, q[mm] >= P[j] - (1 - w[mm])); @constraint(m, q[mm] >= 0)
            else
                @constraint(m, w[mm] == 0); @constraint(m, q[mm] == 0)
            end
        end
        @constraint(m, sum(w) == 1)
        for mm in 1:4
            if mm in Ej; @constraint(m, pre[mm] + P[j] <= τ)
            else;        @constraint(m, pre[mm] + P[j] >= τ); end
        end
        for mm in 1:4; ℓ[mm] += q[mm]; end
    end
    @variable(m, z[1:4], Bin); @constraint(m, sum(z) == 1)
    if level < Inf
        for mm in 1:4; @constraint(m, ℓ[mm] >= level - BIGM * (1 - z[mm])); end
        set_objective_sense(m, MOI.FEASIBILITY_SENSE)
        t0 = time(); optimize!(m); el = time() - t0
        return 0.0, el, termination_status(m)
    else
        @variable(m, t)
        for mm in 1:4; @constraint(m, t <= ℓ[mm] + BIGM * (1 - z[mm])); end
        @objective(m, Max, t)
        t0 = time(); optimize!(m); el = time() - t0
        st = termination_status(m)
        return (st == OPTIMAL ? objective_value(m) : NaN), el, st
    end
end

# ---------------- 便捷包装（与原脚本兼容） ----------------
function piece_reaches(k::Vector{Int}, masks::Vector{Int}, level::Float64;
                       timelimit::Float64 = 300.0, preds::Symbol = :card, cuts::Bool = false)
    for mm in 1:4
        _, _, st = milp_piece(k, masks; heaviest = mm, level = level, timelimit = timelimit,
                              preds = preds, cuts = cuts)
        st == OPTIMAL && return true
    end
    return false
end

function piece_ceiling_milp(k::Vector{Int}, masks::Vector{Int}; timelimit::Float64 = 300.0, preds::Symbol = :card)
    best = NaN
    for mm in 1:4
        v, _, st = milp_piece(k, masks; heaviest = mm, timelimit = timelimit, preds = preds)
        (st == OPTIMAL && (isnan(best) || v > best)) && (best = v)
    end
    return best
end

function piece_feasible(k::Vector{Int}, masks::Vector{Int}; timelimit::Float64 = 60.0, preds::Symbol = :card)
    _, _, st = milp_piece(k, masks; heaviest = 0, timelimit = timelimit, preds = preds)
    return st == OPTIMAL
end

function main()
    mode = length(ARGS) >= 3 ? ARGS[3] : "old"
    k = parse.(Int, split(ARGS[1])); masks = parse.(Int, split(ARGS[2]))
    if mode == "sel"
        v, el, st = milp_sel(k, masks)
        println("milp_sel  天花板 = ", round(v, digits = 8), "  状态=", st, "  用时 ", round(el, digits = 3), " s")
    elseif mode == "seq"
        v, el, st = seq_milp(masks)
        println("seq_milp  天花板 = ", round(v, digits = 8), "  状态=", st, "  用时 ", round(el, digits = 3), " s")
    else
        c = piece_ceiling_milp(k, masks)
        println("原版(4 次) 天花板 = ", round(c, digits = 8))
    end
end

abspath(PROGRAM_FILE) == abspath(@__FILE__) && main()
