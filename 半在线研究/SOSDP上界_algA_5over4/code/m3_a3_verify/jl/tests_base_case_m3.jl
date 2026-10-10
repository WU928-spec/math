include("common.jl")
using JuMP, HiGHS
using Printf

# ---------------------------------------------------------------- helpers
# 把 Python 版“系数向量”(1-based 下标) 转成 common.jl 的 Row（等价于 term）
function row(v::AbstractVector{<:Real})
    r = Tuple{Int,Float64}[]
    for (i, coef) in enumerate(v)
        if abs(coef) > 1e-15
            push!(r, (i, Float64(coef)))
        end
    end
    return r
end

# Python 的 cons 列表 [(vec, rhs), ...] -> common.jl 的 extra [(row, ub), ...]
to_extra(cons) = [(row(v), rhs) for (v, rhs) in cons]

const Branch = Tuple{String, Vector{Tuple{Row,Float64}}, Vector{Row}}

# ---------------------------------------------------------------- 分支枚举（忠实移植）
function build_branches(n::Int)
    if n == 3
        return Branch[
            ("n3", Tuple{Row,Float64}[],
             Row[row([1.0,0.0,0.0]), row([0.0,1.0,0.0]), row([0.0,0.0,1.0])])
        ]
    end
    if n == 4
        return Branch[
            ("n4_L0p1_T",
             to_extra([([-1.0,0.0,1.0,1.0],0.0), ([1.0-C_TARGET,0.0,0.0,1.0],0.0)]),
             Row[row([1.0,0.0,0.0,1.0]), row([0.0,1.0,0.0,0.0]), row([0.0,0.0,1.0,0.0])]),
            ("n4_L0p1_F",
             to_extra([([-1.0,0.0,1.0,1.0],0.0), ([C_TARGET-1.0,0.0,0.0,-1.0],0.0)]),
             Row[row([1.0,0.0,0.0,0.0]), row([0.0,1.0,0.0,0.0]), row([0.0,0.0,1.0,1.0])]),
            ("n4_L0p34_T",
             to_extra([([1.0,0.0,-1.0,-1.0],0.0), ([1.0,0.0,-C_TARGET,1.0-C_TARGET],0.0)]),
             Row[row([1.0,0.0,0.0,1.0]), row([0.0,1.0,0.0,0.0]), row([0.0,0.0,1.0,0.0])]),
            ("n4_L0p34_F",
             to_extra([([1.0,0.0,-1.0,-1.0],0.0), ([-1.0,0.0,C_TARGET,C_TARGET-1.0],0.0)]),
             Row[row([1.0,0.0,0.0,0.0]), row([0.0,1.0,0.0,0.0]), row([0.0,0.0,1.0,1.0])]),
        ]
    end
    # n == 5
    br = Branch[]
    # 步骤 2 条件为真
    push!(br, ("n5_L0p1_T",
        to_extra([([-1.0,0.0,1.0,1.0,0.0],0.0), ([1.0-C_TARGET,0.0,0.0,1.0,0.0],0.0)]),
        Row[row([1.0,0.0,0.0,1.0,0.0]), row([0.0,1.0,0.0,0.0,1.0]), row([0.0,0.0,1.0,0.0,0.0])]))
    push!(br, ("n5_L0p34_T",
        to_extra([([1.0,0.0,-1.0,-1.0,0.0],0.0), ([1.0,0.0,-C_TARGET,1.0-C_TARGET,0.0],0.0)]),
        Row[row([1.0,0.0,0.0,1.0,0.0]), row([0.0,1.0,0.0,0.0,1.0]), row([0.0,0.0,1.0,0.0,0.0])]))

    # 步骤 2 条件为假
    e1p5 = [1.0,0.0,0.0,0.0,1.0]
    loads_true = [[1.0,0.0,0.0,0.0,1.0],[0.0,1.0,0.0,0.0,0.0],[0.0,0.0,1.0,1.0,0.0]]
    loads_M2   = [[1.0,0.0,0.0,0.0,0.0],[0.0,1.0,0.0,0.0,1.0],[0.0,0.0,1.0,1.0,0.0]]
    loads_M3   = [[1.0,0.0,0.0,0.0,0.0],[0.0,1.0,0.0,0.0,0.0],[0.0,0.0,1.0,1.0,1.0]]

    cases = [
        ("L0p1",
         ([-1.0,0.0,1.0,1.0,0.0],0.0),
         ([C_TARGET-1.0,0.0,0.0,-1.0,0.0],0.0),
         [
           ("Lp1_m1", [([-1.0,1.0,0.0,0.0,1.0],0.0), ([0.0,1.0,-1.0,-1.0,0.0],0.0)], [1.0,0.0,0.0,0.0,0.0]),
           ("Lp1_m2", [([-1.0,0.0,1.0,1.0,1.0],0.0), ([0.0,-1.0,1.0,1.0,0.0],0.0)], [1.0,0.0,0.0,0.0,0.0]),
           ("Lm1",    [([1.0,-1.0,0.0,0.0,-1.0],0.0), ([0.0,1.0,-1.0,-1.0,0.0],0.0)], [0.0,1.0,0.0,0.0,1.0]),
           ("Lm2",    [([1.0,0.0,-1.0,-1.0,-1.0],0.0), ([0.0,-1.0,1.0,1.0,0.0],0.0)], [0.0,0.0,1.0,1.0,1.0]),
         ]),
        ("L0p34",
         ([1.0,0.0,-1.0,-1.0,0.0],0.0),
         ([-1.0,0.0,C_TARGET,C_TARGET-1.0,0.0],0.0),
         [
           ("Lp34_m1", [([0.0,1.0,-1.0,-1.0,1.0],0.0), ([0.0,1.0,-1.0,-1.0,0.0],0.0)], [0.0,0.0,1.0,1.0,0.0]),
           ("Lp34_m2", [([0.0,0.0,0.0,0.0,1.0],0.0), ([0.0,-1.0,1.0,1.0,0.0],0.0)], [0.0,0.0,1.0,1.0,0.0]),
           ("Lm1",     [([0.0,-1.0,1.0,1.0,-1.0],0.0), ([0.0,1.0,-1.0,-1.0,0.0],0.0)], [0.0,1.0,0.0,0.0,1.0]),
           ("Lm2",     [([0.0,0.0,0.0,0.0,-1.0],0.0), ([0.0,-1.0,1.0,1.0,0.0],0.0)], [0.0,0.0,1.0,1.0,1.0]),
         ]),
    ]

    for (cname, base, cf, Lcases) in cases
        for (lname, lcons, Lvec) in Lcases
            cons = vcat([base, cf], lcons)
            ct  = [e1p5[k] - C_TARGET*Lvec[k] for k in 1:5]   # p1+p5 <= c L
            cf_ = [C_TARGET*Lvec[k] - e1p5[k] for k in 1:5]   # p1+p5 >= c L
            push!(br, ("n5_$(cname)_$(lname)_S3T",
                to_extra(vcat(cons, [(ct, 0.0)])),
                Row[row(l) for l in loads_true]))
            push!(br, ("n5_$(cname)_$(lname)_S3F_M1",
                to_extra(vcat(cons, [(cf_, 0.0), ([1.0,-1.0,0.0,0.0,0.0],0.0), ([1.0,0.0,-1.0,-1.0,0.0],0.0)])),
                Row[row(l) for l in loads_true]))
            push!(br, ("n5_$(cname)_$(lname)_S3F_M2",
                to_extra(vcat(cons, [(cf_, 0.0), ([-1.0,1.0,0.0,0.0,0.0],0.0), ([0.0,1.0,-1.0,-1.0,0.0],0.0)])),
                Row[row(l) for l in loads_M2]))
            push!(br, ("n5_$(cname)_$(lname)_S3F_M3",
                to_extra(vcat(cons, [(cf_, 0.0), ([-1.0,0.0,1.0,1.0,0.0],0.0), ([0.0,-1.0,1.0,1.0,0.0],0.0)])),
                Row[row(l) for l in loads_M3]))
        end
    end
    return br
end

# ---------------------------------------------------------------- 求解
"""对一个分支：分别最大化每台机器负载，取最大。返回 (值, 见证 p)。"""
function run_branch(n::Int, parts, loads::Vector{Row}, extra)
    objectives = [[l] for l in loads]
    res = solve_lp(n=n, parts=parts, objectives=objectives, low=0.0, extra=extra)
    vals = [r[1] for r in res]
    bi = argmax(vals)
    return vals[bi], res[bi][2]
end

"""统计 LP 状态既非 OPTIMAL 也非 INFEASIBLE 的次数（solve_lp 不暴露状态，故单独计数）。"""
function count_anomalies(n::Int, parts, loads::Vector{Row}, extra)
    cnt = 0
    for blocks in parts
        model = Model(HiGHS.Optimizer); set_silent(model)
        @variable(model, p[1:n])
        for i in 1:n
            set_lower_bound(p[i], 0.0)
        end
        for blk in blocks
            @constraint(model, sum(p[i] for i in blk) <= 1.0)
        end
        for i in 1:(n-1)
            @constraint(model, p[i] >= p[i+1])
        end
        for (r, b) in extra
            @constraint(model, expr(p, r) <= b)
        end
        for l in loads
            @objective(model, Max, expr(p, l))
            optimize!(model)
            st = termination_status(model)
            if st != OPTIMAL && st != INFEASIBLE
                cnt += 1
            end
        end
    end
    return cnt
end

function fmt_witness(p)
    return "[" * join([@sprintf("%.4f", v) for v in p], ", ") * "]"
end

function verify(p::Vector{Float64}, label::String)
    a = a3_sim(copy(p))[1]
    o = brute_opt(copy(p), 3)
    ratio = a / o
    ok = abs(ratio - C_TARGET) < 1e-9
    println(rpad(label, 28), " a3=", @sprintf("%.12f", a),
            "  C*=", @sprintf("%.12f", o),
            "  ratio=", @sprintf("%.12f", ratio),
            ok ? "  ✓ = c" : "  ✗ != c")
    return ok
end

# ---------------------------------------------------------------- 主流程
function main()
    println("c = ", @sprintf("%.15f", C_TARGET))
    println("="^90)

    results = NamedTuple[]
    ok_all = true

    for n in (3, 4, 5)
        parts = partitions(n, n, 3)
        branches = build_branches(n)

        per_branch = [(name=br[1], val=0.0, witness=Float64[]) for br in branches]
        anomalies_total = 0
        for (i, br) in enumerate(branches)
            val, witness = run_branch(n, parts, br[3], br[2])
            per_branch[i] = (name=br[1], val=val, witness=witness)
            anomalies_total += count_anomalies(n, parts, br[3], br[2])
        end

        sorted = sort(per_branch; by = b -> -b.val)
        println()
        println("### n = $n")
        println("branches (name : optimal value):")
        for b in sorted
            println("  ", rpad(b.name, 30), @sprintf("%.12f", b.val))
        end

        # 达到上确界的分支：取建序最靠前的一个（并列时，与 Python 的稳定排序一致）
        bi = 1
        for i in 2:length(per_branch)
            if per_branch[i].val > per_branch[bi].val + 1e-15
                bi = i
            end
        end
        R = per_branch[bi].val
        println("achieving branch: ", per_branch[bi].name)
        println("R_$n = ", @sprintf("%.9f", R), "   (R_$n / c = ", @sprintf("%.12f", R / C_TARGET), ")")
        println("witness p = ", fmt_witness(per_branch[bi].witness))
        println("anomalies (non-optimal LP statuses): ", anomalies_total)

        if n in (4, 5)
            w = per_branch[bi].witness
            a = a3_sim(copy(w))[1]
            o = brute_opt(copy(w), 3)
            println("  LP-witness check: a3=", @sprintf("%.12f", a),
                    "  C*=", @sprintf("%.12f", o),
                    "  ratio=", @sprintf("%.12f", a / o))
        end

        push!(results, (n=n, R=R, branch=per_branch[bi].name,
                        witness=per_branch[bi].witness, anomalies=anomalies_total))
    end

    println()
    println("="^90)
    println("witness verification (a3_sim vs brute_opt), exact instances:")
    ok_all &= verify([1.0, C_TARGET-1.0, C_TARGET-1.0, C_TARGET-1.0],
                     "n=4 p=(1,c-1,c-1,c-1)")
    ok_all &= verify([1.0, C_TARGET-1.0, C_TARGET-1.0, C_TARGET-1.0, 0.0],
                     "n=5 p=(1,c-1,c-1,c-1,0)")

    println()
    println("="^90)
    println("SUMMARY")
    println(rpad("n", 4), rpad("R_n", 16), rpad("achieving branch", 30),
            rpad("witness (4dp)", 44), "anomalies")
    for r in results
        println(rpad(string(r.n), 4),
                rpad(@sprintf("%.9f", r.R), 16),
                rpad(r.branch, 30),
                rpad(fmt_witness(r.witness), 44),
                r.anomalies)
    end

    R3 = results[1].R; R4 = results[2].R; R5 = results[3].R
    ok3 = abs(R3 - 1.0) < 1e-9
    ok4 = abs(R4 - C_TARGET) < 1e-9
    ok5 = abs(R5 - C_TARGET) < 1e-9
    ok_anom = all(r.anomalies == 0 for r in results)
    ok_all &= ok3 & ok4 & ok5 & ok_anom

    println()
    if ok_all
        println("BASE CASE OK")
    else
        println("BASE CASE FAIL")
        ok3     || println("  R_3 mismatch: got ", R3, " want 1.0")
        ok4     || println("  R_4 mismatch: got ", R4, " want ", C_TARGET)
        ok5     || println("  R_5 mismatch: got ", R5, " want ", C_TARGET)
        ok_anom || println("  anomalies != 0")
    end
end

main()
