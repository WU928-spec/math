# a4_razor_cert.jl —— razor 紧 (u,x) 组合的精确有理对偶证书
#   老项目流程：LP（全部约束显式 ≤ 形）→ HiGHS 求解 → 抽对偶 → rationalize →
#   Rational{BigInt} 精确验证：A^T y == c（对偶可行）、y ≥ 0、b^T y == 6/5（界恰为目标）。
#   用法：julia --project=. a4_razor_cert.jl <ui∈1..6>   （每个紧指派一次运行，守 8 分钟纪律）
using JuMP, HiGHS

const RR = Rational{BigInt}
const NVAR = 11                       # (P1..P10, t)

const TIGHT_U = [
    [[1, 9], [2, 5], [3, 6], [4, 7, 8]],
    [[1, 9], [2, 6], [3, 5], [4, 7, 8]],
    [[1, 8], [2, 5], [3, 6], [4, 7, 9]],
    [[1, 8], [2, 6], [3, 5], [4, 7, 9]],
    [[1, 7], [2, 5], [3, 6], [4, 8, 9]],
    [[1, 7], [2, 6], [3, 5], [4, 8, 9]],
]

# ---- 约束构建（显式 ≤ 形，变量 (P1..P10, t)）；返回 rows::Vector{Pair{Vector{RR}, RR}}
function build_rows(assign, pat)
    rows = Pair{Vector{RR}, RR}[]
    function row(pairs, b)
        a = zeros(RR, NVAR)
        for (i, c) in pairs; a[i] += RR(c); end
        push!(rows, a => RR(b))
    end
    for i in 1:9; row([(i, -1), (i + 1, 1)], 0); end          # 秩序 P_i ≥ P_{i+1}
    for i in 1:10
        row([(i, 1)], 1)                                       # 上界
        row([(i, -1)], -RR(4, 15))                             # 下界 4/15
    end
    row([(i, 1) for i in 1:10], 4)                             # Σp ≤ 4
    row([(10, 1)], RR(1, 3))                                   # z ≤ 1/3
    for mm in 1:4                                              # H：ℓ_m ≥ 6/5 − z ⟺ −ℓ_m − z ≤ −6/5
        row([[ (i, -1) for i in assign[mm] ]; [(10, -1)]], -RR(6, 5))
    end
    for b in 1:4                                               # 装箱：固定模式的箱和 ≤ 1
        blk = findall(==(b), pat)
        isempty(blk) || row([(i, 1) for i in blk], 1)
    end
    for mm in 1:4                                              # t ≤ ℓ_m + z
        row([[ (i, -1) for i in assign[mm] ]; [(10, -1)]; [(11, 1)]], 0)
    end
    return rows
end

function solve_lp(rows)
    m = Model(HiGHS.Optimizer); set_silent(m)
    @variable(m, X[1:NVAR])
    refs = [@constraint(m, sum(a[i] * X[i] for i in 1:NVAR) <= b) for (a, b) in rows]
    @objective(m, Max, X[11])
    optimize!(m)
    termination_status(m) == OPTIMAL || return (NaN, Float64[])
    return objective_value(m), dual.(refs)
end

"精确验证：A^T y == c（对偶可行）、y ≥ 0、b^T y == 6/5；自动尝试正负号约定；返回 (ok, 诊断, y)"
function verify_cert(rows, yf)
    c = zeros(RR, NVAR); c[11] = 1
    for sgn in (1, -1)
        y = sgn .* rationalize.(BigInt, yf, 1e-9)
        lhs = zeros(RR, NVAR)
        rhs = zero(RR)
        for ((a, b), yj) in zip(rows, y)
            lhs .+= yj .* a
            rhs += yj * b
        end
        ok_feas = all(lhs .== c)
        ok_nonneg = all(y .>= 0)
        ok_val = (rhs == RR(6, 5))
        ok_feas && ok_nonneg && ok_val && return (true, "符号=$(sgn == 1 ? "+" : "-")", y)
    end
    return (false, "两种符号约定都未通过", RR[])
end

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

function main()
    ui = parse(Int, ARGS[1])
    assign = TIGHT_U[ui]
    pats = gen_patterns_canonical()
    ncert = 0; nfail = 0; ntot = 0
    out = IOStream[]
    open("razor_certs_u$(ui).txt", "w") do io
        for pat in pats
            rows = build_rows(assign, pat)
            v, yf = solve_lp(rows)
            isnan(v) && continue
            ntot += 1
            v > 1.2 - 1e-6 || continue          # 只要 razor-tight
            ncert += 1
            ok, diag, _ = verify_cert(rows, yf)
            ok || (nfail += 1)
            println(io, "pat=$pat sup=$(v) 验证=$ok  $diag")
            ok || println("  !! 验证失败 pat=$pat  $diag")
        end
    end
    println("u$(ui)：可行模式 $(ntot)，razor-tight 证书 $(ncert) 张，验证失败 $(nfail)")
end

main()
