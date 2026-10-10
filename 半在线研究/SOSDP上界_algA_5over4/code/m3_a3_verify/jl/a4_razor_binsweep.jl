# a4_razor_binsweep.jl —— razor 6 种紧指派 × 全部装箱模式的纯 LP sup 扫描
#   目的：razor 严谨证书的规模确认——看每个紧指派下 razor-tight 的装箱模式数
#   装箱模式：10 件 → 4 个无标号箱、每箱 ≤3 件、p1 固定箱 1（首现递增去对称）
using JuMP, HiGHS

function gen_patterns_canonical(n = 10)
    pats = Vector{Int}[]
    cur = zeros(Int, n); cur[1] = 1
    function rec(i)
        if i > n
            push!(pats, copy(cur)); return
        end
        nb = maximum(cur[1:(i-1)])
        for b in 1:min(nb + 1, 4)
            count(==(b), cur[1:(i-1)]) >= 3 && continue
            cur[i] = b; rec(i + 1)
        end
    end
    rec(2)
    return pats
end

function lp_sup(pat, assign)
    n = 10
    m = Model(HiGHS.Optimizer); set_silent(m)
    @variable(m, 4 / 15 <= P[1:n] <= 1.0)
    for i in 1:(n-1); @constraint(m, P[i] >= P[i+1]); end
    @constraint(m, sum(P) <= 4.0)
    @constraint(m, P[n] <= 1 / 3)
    ℓ = [sum(P[i] for i in assign[mm]) for mm in 1:4]
    for mm in 1:4; @constraint(m, ℓ[mm] >= 6 / 5 - P[n]); end   # H（sup 语义等价）
    for b in 1:4
        blk = findall(==(b), pat)
        isempty(blk) && continue
        @constraint(m, sum(P[i] for i in blk) <= 1.0)
    end
    @variable(m, t)
    for mm in 1:4; @constraint(m, t <= ℓ[mm] + P[n]); end
    @objective(m, Max, t)
    optimize!(m)
    termination_status(m) == OPTIMAL || return NaN
    return objective_value(m)
end

const TIGHT_U = [
    [[1, 9], [2, 5], [3, 6], [4, 7, 8]],
    [[1, 9], [2, 6], [3, 5], [4, 7, 8]],
    [[1, 8], [2, 5], [3, 6], [4, 7, 9]],
    [[1, 8], [2, 6], [3, 5], [4, 7, 9]],
    [[1, 7], [2, 5], [3, 6], [4, 8, 9]],
    [[1, 7], [2, 6], [3, 5], [4, 8, 9]],
]

function main()
    pats = gen_patterns_canonical()
    println("装箱模式总数 = ", length(pats), "；紧指派数 = ", length(TIGHT_U))
    for (ui, assign) in enumerate(TIGHT_U)
        ntight = 0; nmid = 0; worst = -Inf
        for pat in pats
            v = lp_sup(pat, assign)
            isnan(v) && continue
            v > worst && (worst = v)
            if v > 1.2 - 1e-6
                ntight += 1
            elseif v > 1.2 - 0.005
                nmid += 1; println("  u$ui 近紧 sup=$(round(v, digits=6)) pat=$pat")
            end
        end
        println("u$(ui) $(assign)：razor-tight 模式 = $(ntight)，近紧 = $(nmid)，max sup = $(round(worst, digits=10))")
        flush(stdout)
    end
end

main()
