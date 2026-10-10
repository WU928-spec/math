# a4_relaxed_bound.jl —— 便宜的"上界证书"：去掉装箱（C*<=1）后的 LP 仍是可行集的超集
#   ⟹ 其最优值 ≥ 真天花板。若 ≤ 阈值，则该片**直接认证通过**（无需 MILP）。
#   用法：julia --project=. a4_relaxed_bound.jl <片清单> <阈值> [只处理前 N 条]
include("a4_lib.jl")
using JuMP, HiGHS

const RHO = C_TARGET
const ALP = 4.0 / 15.0

"松弛上界：family + 轨迹 + Σp<=4 + 计数必要条件，但不含装箱"
function relaxed_bound(k::Vector{Int}, masks::Vector{Int})
    n = 4 + length(k)
    best = NaN
    for mstar in 1:4
        m = Model(HiGHS.Optimizer); set_silent(m)
        @variable(m, P[1:n])
        for i in 1:n; set_lower_bound(P[i], ALP); end
        for i in 1:(n-1); @constraint(m, P[i] >= P[i+1]); end
        @constraint(m, P[4] + P[5] >= P[1])
        @constraint(m, P[2] <= P[3] + P[4])
        @constraint(m, P[3] <= P[4] + P[5])
        @constraint(m, P[5] <= P[3])
        @constraint(m, sum(P) <= 4.0)
        @constraint(m, P[5] <= 0.5)
        n >= 9 && @constraint(m, P[9] <= 1.0 / 3.0)
        τ = RHO * (P[4] + P[5])
        ℓ = [AffExpr(0.0) for _ in 1:4]; for mm in 1:4; ℓ[mm] += P[mm]; end
        for c in 1:length(k)
            j = 4 + c
            Ej = [mm for mm in 1:4 if (masks[c] >> (mm - 1)) & 1 == 1]; aj = k[c]
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
        for mm in 1:4; mm == mstar && continue; @constraint(m, ℓ[mstar] >= ℓ[mm]); end
        @objective(m, Max, ℓ[mstar]); optimize!(m)
        if termination_status(m) == OPTIMAL
            v = objective_value(m); (isnan(best) || v > best) && (best = v)
        end
    end
    return best
end

function main()
    path = ARGS[1]; level = parse(Float64, ARGS[2])
    maxlines = length(ARGS) >= 3 ? parse(Int, ARGS[3]) : typemax(Int)
    lines = readlines(path)
    certified = 0; needmilp = String[]; n = 0; t0 = time()
    for (idx, ln) in enumerate(lines)
        idx > maxlines && break
        f = parse.(Int, split(ln, '\t')); mid = div(length(f), 2)
        b = relaxed_bound(f[1:mid], f[mid+1:end]); n += 1
        if !isnan(b) && b <= level + 1e-9
            certified += 1
        else
            push!(needmilp, ln)
        end
    end
    println("共 ", n, " 条：松弛上界 ≤ ", level, " 而直接认证 ", certified,
            " 条（", round(100 * certified / max(n, 1), digits = 1), "%），需 MILP 复核 ", length(needmilp),
            " 条；用时 ", round(time() - t0, digits = 1), " s")
    open("need_milp.txt", "w") do io
        for r in needmilp; println(io, r); end
    end
    println("待复核片已写入 need_milp.txt")
end
main()
