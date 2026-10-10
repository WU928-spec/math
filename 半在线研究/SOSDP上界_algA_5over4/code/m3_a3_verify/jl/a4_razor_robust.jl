# a4_razor_robust.jl —— razor 紧指派下"H 放宽 δ" 的鲁棒性扫描
#   目的：验证"其余 9082 个装箱模式不可行"的浮点判定是稳健的——
#   把 H 放宽 δ=0.01 后若仍全部不可行/或可行 sup 不超界，则浮点不可行判定可信。
#   用法：julia --project=. a4_razor_robust.jl <ui∈1..6>
using JuMP, HiGHS

const TIGHT_U = [
    [[1, 9], [2, 5], [3, 6], [4, 7, 8]],
    [[1, 9], [2, 6], [3, 5], [4, 7, 8]],
    [[1, 8], [2, 5], [3, 6], [4, 7, 9]],
    [[1, 8], [2, 6], [3, 5], [4, 7, 9]],
    [[1, 7], [2, 5], [3, 6], [4, 8, 9]],
    [[1, 7], [2, 6], [3, 5], [4, 8, 9]],
]

function gen_patterns_canonical(n = 10)
    pats = Vector{Int}[]
    cur = zeros(Int, n); cur[1] = 1
    function rec(i)
        if i > n; push!(pats, copy(cur)); return; end
        nb = maximum(cur[1:(i-1)])
        for b in 1:min(nb + 1, 4)
            count(==(b), cur[1:(i-1)]) >= 3 && continue
            cur[i] = b; rec(i + 1)
        end
    end
    rec(2)
    return pats
end

function lp_sup(pat, assign, δ)
    n = 10
    m = Model(HiGHS.Optimizer); set_silent(m)
    @variable(m, 4 / 15 <= P[1:n] <= 1.0)
    for i in 1:(n-1); @constraint(m, P[i] >= P[i+1]); end
    @constraint(m, sum(P) <= 4.0)
    @constraint(m, P[n] <= 1 / 3)
    ℓ = [sum(P[i] for i in assign[mm]) for mm in 1:4]
    for mm in 1:4; @constraint(m, ℓ[mm] >= 6 / 5 - P[n] - δ); end   # H 放宽 δ
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

function main()
    ui = parse(Int, ARGS[1])
    δ = length(ARGS) >= 2 ? parse(Float64, ARGS[2]) : 0.01
    assign = TIGHT_U[ui]
    pats = gen_patterns_canonical()
    nfeas = 0; worst = -Inf; worstpat = Int[]
    for pat in pats
        v = lp_sup(pat, assign, δ)
        isnan(v) && continue
        nfeas += 1
        if v > worst; worst = v; worstpat = pat; end
    end
    println("u$(ui) δ=$(δ)：可行模式 $(nfeas)/9100，最大 sup = $(round(worst, digits=8))，最差模式 $(worstpat)")
end

main()
