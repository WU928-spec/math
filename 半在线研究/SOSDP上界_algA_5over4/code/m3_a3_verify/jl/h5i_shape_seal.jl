# h5i_shape_seal.jl —— 伪见证形状的 H5i 轨迹约束逐片封底（sup(min_pre+z)，z 兜底）
#   用法：julia --project=. h5i_shape_seal.jl <n> <c1,c2,c3,c4> <outfile> [k5fix] [mask5fix]
#   轨迹片 = (k[5..n], masks[5..n])；H5i 规则：步5 fullest；1∈E5⟺regime F（步6起 fullest），否则 regime L（步6起 lightest）；
#   mask=0 ⟹ 兜底 argmin。z=pn 只枚举 mask=0（兜底）。剪枝：计数余量 + M4 未收件 ⟹ 4∈E + 前缀可行性 MILP。
include("a4_lib.jl")
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
    @variable(m, y[1:J, 1:4] >= 0)
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

# 一体化叶构造（避免 JuMP 变量数组扩容问题）：直接建 items 1..n 全模型，z 步约束按兜底写
function leaf_model(n::Int, k::Vector{Int}, masks::Vector{Int}, mode::Symbol)
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
    @objective(m, Max, ℓ[r])                  # ℓ[r] 已含 z ⟹ = pre[r] + z
    optimize!(m)
    st = termination_status(m)
    return (st == OPTIMAL) ? objective_value(m) : NaN, st
end

function main()
    n = parse(Int, ARGS[1])
    cnt = parse.(Int, split(ARGS[2], ","))
    outfile = ARGS[3]
    k5fix = length(ARGS) >= 4 ? parse(Int, ARGS[4]) : 0
    mask5fix = length(ARGS) >= 5 ? parse(Int, ARGS[5]) : -1
    sum(cnt) == n - 1 || error("cnt 之和必须 = n−1")
    t0 = time()
    leaves = 0; feas_leaves = 0; nodes = 0; pruned = 0
    best = -Inf; bestpiece = ""
    io = open(outfile, "w")
    println(io, "# H5i 形状封底 n=$n cnt=$cnt  ρ=$RHO")
    flush(io)
    kk = Int[]; mk = Int[]
    function dfs(j::Int, cntleft::Vector{Int}, m4done::Bool, mode::Symbol)
        sum(cntleft) > n - j && return            # 剩余步数（j..n−1）放不下计数余量
        if j == n
            # z 步：mask=0，接收机 r=1..4（argmin 由 LP 约束保证）
            any(>(0), cntleft) && return           # 计数未耗尽 ⟹ 不是本形状
            for r in 1:4
                leaves += 1
                v, st = leaf_model(n, vcat(kk, r), vcat(mk, 0), mode)
                if !isnan(v)
                    feas_leaves += 1
                    if v > best + 1e-12
                        best = v
                        bestpiece = "k=$(join(vcat(kk, r), ",")) masks=$(join(vcat(mk, 0), ",")) mode=$mode"
                    end
                    @printf(io, "leaf k=%s masks=%s mode=%s sup=%.6f\n", join(vcat(kk, r), ","),
                            join(vcat(mk, 0), ","), mode, v)
                    flush(io)
                end
            end
            return
        end
        maskrange = m4done ? (0:15) : (8:15)    # M4 未收件 ⟹ 4∈E（M4 恒合格）
        for mask in maskrange
            (j == 5 && mask5fix >= 0 && mask != mask5fix) && continue
            E = eset(mask)
            # 步 5：fullest + 并列小下标 ⟹ 1∈E5 时接收机恒为 1
            arec = isempty(E) ? (1:4) : E
            for a in arec
                (j == 5 && 1 in E && a != 1) && continue
                (j == 5 && k5fix > 0 && a != k5fix) && continue
                cntleft[a] <= 0 && continue
                mode2 = j == 5 ? ((1 in E) ? :F : :L) : mode
                push!(kk, a); push!(mk, mask)
                nodes += 1
                if piece_feas(kk, mk, mode2)
                    cntleft[a] -= 1
                    dfs(j + 1, cntleft, m4done || a == 4, mode2)
                    cntleft[a] += 1
                else
                    pruned += 1
                end
                pop!(kk); pop!(mk)
            end
        end
    end
    dfs(5, cnt .- 1, false, :open)
    @printf(io, "# DONE n=%d cnt=%s 叶 %d 可行叶 %d 节点 %d 剪 %d 最大sup=%.8f (ρ=%.8f) 片=%s 用时 %.1fs\n",
            n, string(cnt), leaves, feas_leaves, nodes, pruned, best, RHO, bestpiece, time() - t0)
    close(io)
    @printf("n=%d cnt=%s 叶 %d 可行叶 %d 最大sup=%.8f 用时 %.1fs\n", n, string(cnt), leaves, feas_leaves, best, time() - t0)
end
main()
