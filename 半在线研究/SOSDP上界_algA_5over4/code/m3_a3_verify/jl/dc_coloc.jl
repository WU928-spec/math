# dc_coloc.jl —— direction C：精确判定"工件对 (i, n) 是否同机"的 MILP（第二版）
#
#   截断等价：对 (i,j)，算法对前 j 件的放置只依赖 p1..pj（τ 只看 p1..p5），截断保持
#   有序、>4/15、C*≤1、分支谓词 ⟹ (i,j) 在某 n≥j 实例同机 ⟺ 在 n=j 家族同机。
#
#   语义 :exact —— 与真实算法（最小下标 tie-break）一致，至多差一个 ε-薄层：
#     · e[j,m]=1 ⟹ ℓ+pj ≤ τ；e=0 ⟹ ℓ+pj ≥ τ+ε      （ε 薄层内的实例不可表示）
#     · 填充步：所选机 m ∈ E 且 ℓ_m ≥ 所有 E 成员、ℓ_m ≥ ℓ_m' + ε 对更小下标 m'∈E
#     · 兜底步：所选机 m 最轻且 ℓ_m ≤ ℓ_m' − ε 对更小下标 m'
#   ⟹ 模型可行 ⟹ 真实同机（再经精确模拟复核）；模型不可行 ⟹ 除 ε 薄层外永不同机。
#   语义 :relaxed —— 并列宽松（任何 tie-break 的超集）：不可行 ⟹ 严格 NEVER（含一切并列）。
#
#   用法：julia --project=. dc_coloc.jl <full45|full1> <n> [tlimit] [exact|relaxed] [eps]
include("a4_lib.jl")
using JuMP, HiGHS

const RHO = C_TARGET
const ALP = 4.0 / 15.0
const BIGM = 4.0

function coloc_model(n::Int, preds::Symbol; semantics::Symbol = :exact, eps::Float64 = 1e-3)
    m = Model(HiGHS.Optimizer); set_silent(m)
    @variable(m, P[1:n])
    for i in 1:n; set_lower_bound(P[i], ALP); set_upper_bound(P[i], 1.0); end
    for i in 1:(n-1); @constraint(m, P[i] >= P[i+1]); end
    if preds == :full1
        @constraint(m, P[1] >= P[4] + P[5]); τ = RHO * P[1]
    else
        @constraint(m, P[4] + P[5] >= P[1]); τ = RHO * (P[4] + P[5])
    end
    @constraint(m, sum(P) <= 4.0)
    @variable(m, x[1:n, 1:4], Bin)
    @variable(m, y[1:n, 1:4])
    for i in 1:n
        @constraint(m, sum(x[i, :]) == 1)
        for b in 1:4
            @constraint(m, y[i, b] <= x[i, b]); @constraint(m, y[i, b] <= P[i])
            @constraint(m, y[i, b] >= P[i] - (1 - x[i, b])); @constraint(m, y[i, b] >= 0)
        end
    end
    for b in 1:4
        @constraint(m, sum(y[i, b] for i in 1:n) <= 1.0)
        @constraint(m, sum(x[i, b] for i in 1:n) <= 3)
    end
    @constraint(m, x[1, 1] == 1)
    @variable(m, c[5:n, 1:4], Bin)
    @variable(m, e[5:n, 1:4], Bin)
    @variable(m, empty[5:n], Bin)
    @variable(m, yA[5:n, 1:4])
    ℓ(j, mm) = P[mm] + sum(yA[i, mm] for i in 5:(j-1); init = 0.0)
    for j in 5:n
        for mm in 1:4
            @constraint(m, yA[j, mm] <= P[j]); @constraint(m, yA[j, mm] <= c[j, mm])
            @constraint(m, yA[j, mm] >= P[j] - (1 - c[j, mm])); @constraint(m, yA[j, mm] >= 0)
        end
        @constraint(m, sum(c[j, :]) == 1)
        @constraint(m, sum(e[j, :]) <= 4 * (1 - empty[j]))
        @constraint(m, sum(e[j, :]) >= 1 - empty[j])
        for mm in 1:4
            pre = ℓ(j, mm)
            @constraint(m, pre + P[j] <= τ + BIGM * (1 - e[j, mm]))
            if semantics == :exact
                @constraint(m, pre + P[j] >= τ + eps - BIGM * e[j, mm])
            else
                @constraint(m, pre + P[j] >= τ - BIGM * e[j, mm])
            end
            @constraint(m, c[j, mm] <= e[j, mm] + empty[j])
            for mp in 1:4
                prem = ℓ(j, mp)
                @constraint(m, pre >= prem - BIGM * (3 - c[j, mm] - e[j, mp] - (1 - empty[j])))
                @constraint(m, pre <= prem + BIGM * (2 - c[j, mm] - empty[j]))
                if semantics == :exact && mp < mm
                    # tie-break：更小下标优先 ⟹ 选 mm 必须严格优于/轻于 mp
                    @constraint(m, pre >= prem + eps - BIGM * (3 - c[j, mm] - e[j, mp] - (1 - empty[j])))
                    @constraint(m, pre <= prem - eps + BIGM * (2 - c[j, mm] - empty[j]))
                end
            end
        end
    end
    q = Dict{Int,VariableRef}()
    for i in 1:(n-1)
        if i <= 4
            q[i] = c[n, i]
        else
            pm = @variable(m, [1:4], binary = true)
            qq = @variable(m, binary = true)
            for mm in 1:4
                @constraint(m, pm[mm] <= c[i, mm]); @constraint(m, pm[mm] <= c[n, mm])
                @constraint(m, pm[mm] >= c[i, mm] + c[n, mm] - 1)
            end
            @constraint(m, qq <= sum(pm))
            for mm in 1:4; @constraint(m, qq >= pm[mm]); end
            q[i] = qq
        end
    end
    return m, P, q, c, empty
end

function sim_coloc(p::Vector{Float64}, i::Int)
    ms, asg, _ = a4_sim(p, A4(C_TARGET, [:p1, :p45], false, false))
    n = length(p)
    return any(mm -> i in asg[mm] && n in asg[mm], 1:4)
end

function run_one(preds::Symbol, n::Int, tlim::Float64; semantics::Symbol = :exact, eps::Float64 = 1e-4,
                 prewit::Set{Int} = Set{Int}())
    println("═══ preds=$preds  n=$n  sem=$semantics eps=$eps ═══"); flush(stdout)
    m, P, q, c, empty = coloc_model(n, preds; semantics = semantics, eps = eps)
    set_time_limit_sec(m, tlim)
    res = Dict{Int,String}()
    for i in 1:(n-1)
        i in prewit && (res[i] = "WITNESS(sample)"; continue)
        con = i <= 4 ? @constraint(m, c[n, i] >= 1) : @constraint(m, q[i] >= 1)
        @objective(m, Max, 0.0 * P[1])
        t0 = time(); optimize!(m)
        st = termination_status(m); el = round(time() - t0, digits = 1)
        if st == INFEASIBLE || st == INFEASIBLE_OR_UNBOUNDED
            res[i] = semantics == :exact ? "NEVER*(ε)" : "NEVER"
            println("  ($i,$n): ", res[i], "  [$(el)s]"); flush(stdout)
        elseif primal_status(m) == FEASIBLE_POINT
            pv = value.(P)
            if sim_coloc(pv, i)
                res[i] = "WITNESS"
                println("  ($i,$n): WITNESS  p=", join(round.(pv, digits=5), " "), "  [$(el)s]"); flush(stdout)
            else
                res[i] = "AMBIG"
                println("  ($i,$n): AMBIG  p=", join(round.(pv, digits=5), " "), "  [$(el)s]"); flush(stdout)
            end
        else
            res[i] = "UNKNOWN($st)"
            println("  ($i,$n): UNKNOWN 状态=$st  [$(el)s]"); flush(stdout)
        end
        delete(m, con)
    end
    # fill/overflow 分类（对 WITNESS）
    for i in 1:(n-1)
        get(res, i, "") == "WITNESS" || continue
        conq = i <= 4 ? @constraint(m, c[n, i] >= 1) : @constraint(m, q[i] >= 1)
        con1 = @constraint(m, empty[n] >= 1); @objective(m, Max, 0.0 * P[1]); optimize!(m)
        ov = primal_status(m) == FEASIBLE_POINT
        delete(m, con1)
        con1 = @constraint(m, empty[n] <= 0); optimize!(m)
        fl = primal_status(m) == FEASIBLE_POINT
        delete(m, con1); delete(m, conq)
        res[i] = "WITNESS[fill=$(fl ? 1 : 0),overflow=$(ov ? 1 : 0)]"
        println("  ($i,$n) 分类: fill=$fl overflow=$ov"); flush(stdout)
    end
    println("── preds=$preds n=$n 汇总：")
    for i in 1:(n-1); println("   ($i,$n): ", get(res, i, "?")); end
    flush(stdout)
    return res
end

function main()
    preds = Symbol(ARGS[1]); n = parse(Int, ARGS[2])
    tlim = length(ARGS) >= 3 ? parse(Float64, ARGS[3]) : 180.0
    sem = length(ARGS) >= 4 ? Symbol(ARGS[4]) : :exact
    eps = length(ARGS) >= 5 ? parse(Float64, ARGS[5]) : 1e-3
    run_one(preds, n, tlim; semantics = sem, eps = eps)
end
abspath(PROGRAM_FILE) == abspath(@__FILE__) && main()
