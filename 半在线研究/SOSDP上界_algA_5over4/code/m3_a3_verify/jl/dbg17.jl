# a4_milp10.jl —— 用"装箱可行性 MILP"求一条片的天花板（含装箱二元变量）
#   max_m ℓ_m 写成：t ≥ ℓ_m (∀m) 且 **最小化** t
#   用法：julia --project=. a4_milp10.jl "<a5..a10>" "<mask5..mask10>"
include("common.jl")
using JuMP, HiGHS

const RHO = C_TARGET
const ALP = 4.0 / 15.0
const NT  = 10

function milp_piece(k::Vector{Int}, masks::Vector{Int}; timelimit::Float64 = 300.0, verbose::Bool = false)
    m = Model(HiGHS.Optimizer); set_silent(m); set_time_limit_sec(m, timelimit)
    @variable(m, P[1:NT])
    for i in 1:NT; set_lower_bound(P[i], ALP); set_upper_bound(P[i], 1.0); end
    for i in 1:(NT-1); @constraint(m, P[i] >= P[i+1]); end
    @constraint(m, P[4] + P[5] >= P[1])                       # Λ = p45 分支
    @constraint(m, P[2] <= P[3] + P[4])                       # 家族谓词
    @constraint(m, P[3] <= P[4] + P[5])
    @constraint(m, P[5] <= P[3])
    @constraint(m, sum(P) <= 4.0)                             # 容量必要界
    SKIPP = get(ENV,"SKIP_PACK","") == "1"
    SKIPT = get(ENV,"SKIP_TRACE","") == "1"
    if !SKIPP
    # ---- 装箱（C* <= 1）：x[i,b] ∈ {0,1}, y[i,b] = x[i,b]·P[i]
    @variable(m, x[1:NT, 1:4], Bin)
    @variable(m, y[1:NT, 1:4])
    for i in 1:NT
        @constraint(m, sum(x[i, :]) == 1)
        for b in 1:4
            @constraint(m, y[i, b] <= x[i, b])
            @constraint(m, y[i, b] <= P[i])
            @constraint(m, y[i, b] >= P[i] - (1 - x[i, b]))
            @constraint(m, y[i, b] >= 0)
        end
    end
    for b in 1:4
        @constraint(m, sum(y[i, b] for i in 1:NT) <= 1.0)
        @constraint(m, sum(x[i, b] for i in 1:NT) <= 3)
    end
    @constraint(m, x[1, 1] == 1)                              # 对称性破缺（箱可互换）
    end # !SKIPP
    if !SKIPT
    # ---- 轨迹约束
    τ = RHO * (P[4] + P[5])
    ℓ = [AffExpr(0.0) for _ in 1:4]; for mm in 1:4; ℓ[mm] += P[mm]; end
    for c in 1:6
        j = 4 + c
        Ej = [mm for mm in 1:4 if (masks[c] >> (mm - 1)) & 1 == 1]
        aj = k[c]
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
    end # !SKIPT
    if SKIPT; ℓ = [AffExpr(0.0) for _ in 1:4]; for mm in 1:4; ℓ[mm] += P[mm]; end; end
    @variable(m, t)
    for mm in 1:4; @constraint(m, t >= ℓ[mm]); end
    @objective(m, Min, t)
    t0 = time(); optimize!(m); el = time() - t0
    st = termination_status(m)
    val = (st == OPTIMAL) ? objective_value(m) : NaN
    verbose && println("  状态=", st, "  用时 ", round(el, digits = 2), " s")
    return val, el, st
end

function main()
    k = parse.(Int, split(ARGS[1])); masks = parse.(Int, split(ARGS[2]))
    println("片: a=", k, " masks=", masks)
    val, el, st = milp_piece(k, masks; verbose = true)
    println("MILP 天花板 = ", round(val, digits = 8), "  状态=", st, "  用时 ", round(el, digits = 2), " s")
end
main()
