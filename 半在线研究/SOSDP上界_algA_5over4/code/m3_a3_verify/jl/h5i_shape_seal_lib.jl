# h5i_shape_seal.jl —— 伪见证形状的 H5i 轨迹约束逐片封底（sup(min_pre+z)，z 兜底）
#   用法：julia --project=. h5i_shape_seal.jl <n> <c1,c2,c3,c4> <outfile> [k5fix] [mask5fix]
#   轨迹片 = (k[5..n], masks[5..n])；H5i 规则：步5 fullest；1∈E5⟺regime F（步6起 fullest），否则 regime L（步6起 lightest）；
#   mask=0 ⟹ 兜底 argmin。z=pn 只枚举 mask=0（兜底）。剪枝：计数余量 + M4 未收件 ⟹ 4∈E + 前缀可行性 MILP。
using JuMP, HiGHS, Printf

const RHO = C_TARGET
const ALP0 = 4 * (RHO - 1) / 3          # 0.24061（失败区件下界）
const BIGM = 6.0

eset(mask::Int) = [mm for mm in 1:4 if (mask >> (mm - 1)) & 1 == 1]

"建 items 1..J 的部分轨迹模型（H5i）；k/masks 对应 j=5..J。返回 (model, P, ℓ)。"
function build_partial(J::Int, k::Vector{Int}, masks::Vector{Int}, mode::Symbol)
    m = Model(HiGHS.Optimizer); set_silent(m); set_time_limit_sec(m, 120.0)
    @variable(m, ALP0 <= P[1:J] <= 1.0)
    for i in 1:(J - 1); @constraint(m, P[i] >= P[i + 1]); end
    @constraint(m, sum(P) <= 4.0)
    @variable(m, x[1:J, 1:4], Bin)

    for i in 1:J
        @constraint(m, sum(x[i, :]) == 1)
        for b in 1:4
            @constraint(m, y[i, b] <= x[i, b]); @constraint(m, y[i, b] <= P[i])
            @constraint(m, y[i, b] >= P[i] - (1 - x[i, b]))
        end
    end
    for b in 1:4
        @constraint(m, sum(y[:, b]) <= 1.0)
        @constraint(m, sum(x[:, b]) <= 4)     # ρ 版：箱至多 4 件
    end
    @constraint(m, x[1, 1] == 1)
    # Λ = max(P1, P4+P5)（精确二元编码）
    @variable(m, lam >= 0)
    @variable(m, blam, Bin)
    @constraint(m, lam >= P[1])
    @constraint(m, lam >= P[4] + P[5])
    @constraint(m, lam <= P[1] + BIGM * blam)
    @constraint(m, lam <= P[4] + P[5] + BIGM * (1 - blam))
    τ = RHO * lam
    ℓ = [AffExpr(0.0) for _ in 1:4]
    for mm in 1:4; ℓ[mm] += P[mm]; end
    for c in 1:length(k)
        j = 4 + c; E = eset(masks[c]); a = k[c]
        pre = copy(ℓ)
        for mm in 1:4
            if mm in E; @constraint(m, pre[mm] + P[j] <= τ)
            else;       @constraint(m, pre[mm] + P[j] >= τ); end
        end
        if isempty(E)
            for mm in 1:4; @constraint(m, pre[a] <= pre[mm]); end
        elseif mode == :F || j == 5
            for mm in E; @constraint(m, pre[a] >= pre[mm]); end
        else
            for mm in E; @constraint(m, pre[a] <= pre[mm]); end
        end
        ℓ[a] += P[j]
    end
    return m, P, ℓ
end

piece_feas(k, masks, mode) = begin
    J = 4 + length(k)
    m, _, _ = build_partial(J, k, masks, mode)
    set_objective_sense(m, MOI.FEASIBILITY_SENSE)
    optimize!(m)
    termination_status(m) == OPTIMAL
end

function leaf_model_wp(n::Int, k::Vector{Int}, masks::Vector{Int}, mode::Symbol)
    # k/masks 长 n−4：j=5..n；masks[n−4] 必为 0（z 兜底）
    m = Model(HiGHS.Optimizer); set_silent(m); set_time_limit_sec(m, 120.0)
    @variable(m, ALP0 <= P[1:n] <= 1.0)
    for i in 1:(n - 1); @constraint(m, P[i] >= P[i + 1]); end
    @constraint(m, P[n] <= 1 / 3)             # z ≤ 1/3（引理 2.1）
    @constraint(m, sum(P) <= 4.0)
    @variable(m, x[1:n, 1:4], Bin)
    @variable(m, y[1:n, 1:4] >= 0)
    for i in 1:n
        @constraint(m, sum(x[i, :]) == 1)
        for b in 1:4
            @constraint(m, y[i, b] <= x[i, b]); @constraint(m, y[i, b] <= P[i])
            @constraint(m, y[i, b] >= P[i] - (1 - x[i, b]))
        end
    end
    for b in 1:4
        @constraint(m, sum(y[:, b]) <= 1.0)
        @constraint(m, sum(x[:, b]) <= 4)
    end
    @constraint(m, x[1, 1] == 1)
    @variable(m, lam >= 0)
    @variable(m, blam, Bin)
    @constraint(m, lam >= P[1])
    @constraint(m, lam >= P[4] + P[5])
    @constraint(m, lam <= P[1] + BIGM * blam)
    @constraint(m, lam <= P[4] + P[5] + BIGM * (1 - blam))
    τ = RHO * lam
    ℓ = [AffExpr(0.0) for _ in 1:4]
    for mm in 1:4; ℓ[mm] += P[mm]; end
    for c in 1:(n - 4)
        j = 4 + c; E = eset(masks[c]); a = k[c]
        pre = copy(ℓ)
        if j < n
            for mm in 1:4
                if mm in E; @constraint(m, pre[mm] + P[j] <= τ)
                else;       @constraint(m, pre[mm] + P[j] >= τ); end
            end
            if isempty(E)
                for mm in 1:4; @constraint(m, pre[a] <= pre[mm]); end
            elseif mode == :F || j == 5
                for mm in E; @constraint(m, pre[a] >= pre[mm]); end
            else
                for mm in E; @constraint(m, pre[a] <= pre[mm]); end
            end
        else
            # z 步：兜底（E=∅ 已由 masks[n−4]=0 保证）+ argmin
            for mm in 1:4
                @constraint(m, pre[mm] + P[j] >= τ)
                @constraint(m, pre[a] <= pre[mm])
            end
        end
        ℓ[a] += P[j]
    end
    # 目标：max min_pre + z = (z 接收机 r 的 pre 负载) + P[n]；r = k[n−4]，其 pre = ℓ − P[n]
    r = k[n - 4]
    @objective(m, Max, ℓ[r])
    optimize!(m)
    st = termination_status(m)
    return (st == OPTIMAL) ? objective_value(m) : NaN, st, (st == OPTIMAL ? value.(P) : Float64[])
end

# ε-内缩版（不合格约束 ≥τ+ε），返回 (sup, p*)
function h5i_eps_witness(n, k, masks, mode, eps)
    m = Model(HiGHS.Optimizer); set_silent(m); set_time_limit_sec(m, 120.0)
    @variable(m, ALP0 <= P[1:n] <= 1.0)
    for i in 1:(n - 1); @constraint(m, P[i] >= P[i + 1]); end
    @constraint(m, P[n] <= 1 / 3)
    @constraint(m, sum(P) <= 4.0)
    @variable(m, x[1:n, 1:4], Bin)
    @variable(m, y[1:n, 1:4] >= 0)
    for i in 1:n
        @constraint(m, sum(x[i, :]) == 1)
        for b in 1:4
            @constraint(m, y[i, b] <= x[i, b]); @constraint(m, y[i, b] <= P[i])
            @constraint(m, y[i, b] >= P[i] - (1 - x[i, b]))
        end
    end
    for b in 1:4
        @constraint(m, sum(y[:, b]) <= 1.0)
        @constraint(m, sum(x[:, b]) <= 4)
    end
    @constraint(m, x[1, 1] == 1)
    @variable(m, lam >= 0)
    @variable(m, blam, Bin)
    @constraint(m, lam >= P[1])
    @constraint(m, lam >= P[4] + P[5])
    @constraint(m, lam <= P[1] + BIGM * blam)
    @constraint(m, lam <= P[4] + P[5] + BIGM * (1 - blam))
    τ = RHO * lam
    ℓ = [AffExpr(0.0) for _ in 1:4]
    for mm in 1:4; ℓ[mm] += P[mm]; end
    for c in 1:(n - 4)
        j = 4 + c; E = eset(masks[c]); a = k[c]
        pre = copy(ℓ)
        if j < n
            for mm in 1:4
                if mm in E; @constraint(m, pre[mm] + P[j] <= τ)
                else;       @constraint(m, pre[mm] + P[j] >= τ + eps); end
            end
            if isempty(E)
                for mm in 1:4; @constraint(m, pre[a] <= pre[mm]); end
            elseif mode == :F || j == 5
                for mm in E; @constraint(m, pre[a] >= pre[mm]); end
            else
                for mm in E; @constraint(m, pre[a] <= pre[mm]); end
            end
        else
            for mm in 1:4
                @constraint(m, pre[mm] + P[j] >= τ + eps)
                @constraint(m, pre[a] <= pre[mm])
            end
        end
        ℓ[a] += P[j]
    end
    r = k[n - 4]
    @objective(m, Max, ℓ[r])
    optimize!(m)
    st = termination_status(m)
    return (st == OPTIMAL ? objective_value(m) : NaN), (st == OPTIMAL ? value.(P) : Float64[])
end
