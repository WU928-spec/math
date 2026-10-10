# a4_prefilter.jl —— 免费筛子：对每条片用"粗界"试直接认证（≤1.2 则无需进 MILP）
#   粗界（对任意轨迹都是合法上界）：ℓ_max ≤ max( τ, max_{j∈F} [ (Σ_{i<j}p_i)/4 + p_j ] )，F = 该片的兜底步。
#   在"家族(无装箱) + 该片轨迹约束"的纯 LP 上对这个式子取最大；≤1.2 ⟹ 该片**直接认证通过**。
#   用法：julia --project=. a4_prefilter.jl <片清单> <level>
include("a4_lib.jl")
include("a4_avg_bound.jl")
using JuMP, HiGHS

function crude_bound(k::Vector{Int}, masks::Vector{Int}, preds::Symbol, tlim::Float64)
    n = 4 + length(k)
    worst = -Inf
    m, P = base_model(n, preds, false)          # 无装箱：纯 LP（更松但仍是合法上界）
    set_time_limit_sec(m, tlim)
    τ = RHO * (P[4] + P[5])
    ℓ = [AffExpr(0.0) for _ in 1:4]; for mm in 1:4; ℓ[mm] += P[mm]; end
    F = Int[]
    for c in 1:length(k)
        j = 4 + c; Ej = [mm for mm in 1:4 if (masks[c] >> (mm - 1)) & 1 == 1]; aj = k[c]
        isempty(Ej) && push!(F, j)
        pre = copy(ℓ)
        for mm in 1:4
            if mm in Ej; @constraint(m, pre[mm] + P[j] <= τ)
            else;        @constraint(m, pre[mm] + P[j] >= τ); end
        end
        if isempty(Ej)
            for mm in 1:4; mm == aj && continue; @constraint(m, pre[aj] <= pre[mm]); end
        else
            for mm in Ej; mm == aj && continue; @constraint(m, pre[aj] >= pre[mm]); end
        end
        ℓ[aj] += P[j]
    end
    # 目标 = max(τ, max_{j∈F} [S_j/4 + p_j])：逐项取最大
    @objective(m, Max, τ); optimize!(m)
    termination_status(m) == OPTIMAL && (worst = max(worst, objective_value(m)))
    for j in F
        m2, P2 = base_model(n, preds, false); set_time_limit_sec(m2, tlim)
        τ2 = RHO * (P2[4] + P2[5]); ℓ2 = [AffExpr(0.0) for _ in 1:4]; for mm in 1:4; ℓ2[mm] += P2[mm]; end
        for c in 1:length(k)
            jj = 4 + c; Ej = [mm for mm in 1:4 if (masks[c] >> (mm - 1)) & 1 == 1]; aj = k[c]
            pre = copy(ℓ2)
            for mm in 1:4
                if mm in Ej; @constraint(m2, pre[mm] + P2[jj] <= τ2)
                else;        @constraint(m2, pre[mm] + P2[jj] >= τ2); end
            end
            if isempty(Ej)
                for mm in 1:4; mm == aj && continue; @constraint(m2, pre[aj] <= pre[mm]); end
            else
                for mm in Ej; mm == aj && continue; @constraint(m2, pre[aj] >= pre[mm]); end
            end
            ℓ2[aj] += P2[jj]
        end
        S = sum(P2[i] for i in 1:(j-1))
        @objective(m2, Max, S / 4 + P2[j]); optimize!(m2)
        termination_status(m2) == OPTIMAL && (worst = max(worst, objective_value(m2)))
    end
    return worst
end

function main()
    path = ARGS[1]; level = parse(Float64, ARGS[2])
    rows = [strip(l) for l in readlines(path) if !isempty(strip(l))]
    cert = 0; need = 0; byF = Dict{Int,Vector{Int}}(); t0 = time()
    for (idx, ln) in enumerate(rows)
        f = parse.(Int, split(ln, '\t')); mid = div(length(f), 2)
        k = f[1:mid]; masks = f[mid+1:end]
        nfb = count(==(0), masks)
        b = crude_bound(k, masks, :card, 60.0)
        ok = (!isnan(b) && b <= level + 1e-9)
        ok ? (cert += 1) : (need += 1)
        v = get!(byF, nfb, [0, 0]); ok ? (v[1] += 1) : (v[2] += 1)
        idx % 500 == 0 && (println("  [进度] ", idx, "/", length(rows), "  已认证 ", cert, "  需MILP ", need, "  ", round(time() - t0, digits = 0), " s"); flush(stdout))
    end
    println("\n合计 ", length(rows), " 条：粗界直接认证 ", cert, "（", round(100cert / length(rows), digits = 1), "%），需进 MILP ", need)
    println("用时 ", round(time() - t0, digits = 1), " s")
    println("按兜底步数分（认证/需MILP）：")
    for nfb in sort(collect(keys(byF)))
        v = byF[nfb]; println("   兜底 ", nfb, " 步: 认证 ", v[1], " / 需MILP ", v[2])
    end
end
main()
