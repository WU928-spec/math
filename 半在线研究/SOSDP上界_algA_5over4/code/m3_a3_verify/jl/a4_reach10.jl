# a4_reach10.jl —— (h) 一次「可达性 MILP」：把 E 集合与放置都做成二元变量，
#   单次求解覆盖整个 n=10、Λ=p4+p5 家族的全部轨迹。
#
#   合法性：两条 big-M 都取 W=6，而约束活动范围 pre+P_j-τ ∈ [-2.4, 5]，
#   故 W 只需大于活动范围即可，**不是** (e) 那种"条件写在边界上"的不可达 big-M。
#   另外这里**丢掉 argmax/argmin**（允许放 E 内任意台/任意台），是合法超集 ⟹ 给出的
#   唯一的松弛是"并列时取哪台"（不影响 sup）。若最优化值 ≤ 1.2 或 level 判定不可行，则该块一次封闭。
#
#   用法：julia --project=. a4_reach10.jl opt        # 最优化：给松弛上界
#         julia --project=. a4_reach10.jl level 1.2  # 判是否存在 ≥ level 的点
include("a4_lib.jl")
include("a4_milp10.jl")

function reach_all(; level::Float64 = Inf, timelimit::Float64 = 600.0, preds::Symbol = :card)
    n = 10
    m, P = _base(n; preds = preds, cuts = false)
    set_time_limit_sec(m, timelimit)
    if get(ENV, "NORM", "") == "p1"
        @constraint(m, P[1] >= 1.0)
    end
    τ = RHO * (P[4] + P[5])
    ℓ = [AffExpr(0.0) for _ in 1:4]
    for mm in 1:4; ℓ[mm] += P[mm]; end
    W = 5.0
    @variable(m, z[1:6, 1:4], Bin)      # z[c,mm]=1 ⟺ mm ∈ E_{4+c}
    @variable(m, s[1:6], Bin)           # s[c]=1 ⟺ E_{4+c} = ∅
    @variable(m, w[1:6, 1:4], Bin)      # 放置：a_{4+c} = mm
    @variable(m, q[1:6, 1:4])           # q = w · p_j
    for c in 1:6
        j = 4 + c
        pre = copy(ℓ)
        for mm in 1:4
            @constraint(m, pre[mm] + P[j] <= τ + W * (1 - z[c, mm]))
            @constraint(m, pre[mm] + P[j] >= τ - W * z[c, mm])
            @constraint(m, z[c, mm] <= 1 - s[c])
            @constraint(m, w[c, mm] <= z[c, mm] + s[c])
            @constraint(m, q[c, mm] <= P[j])
            @constraint(m, q[c, mm] <= w[c, mm])
            @constraint(m, q[c, mm] >= P[j] - (1 - w[c, mm]))
            @constraint(m, q[c, mm] >= 0)
        end
        @constraint(m, sum(w[c, mm] for mm in 1:4) == 1)
        @constraint(m, sum(z[c, mm] for mm in 1:4) >= 1 - s[c])
        # argmax（E 非空）：选中的那台在 E 内负载最大；argmin（E 空）：负载最小
        for mm in 1:4, m2 in 1:4
            mm == m2 && continue
            @constraint(m, pre[mm] >= pre[m2] - W * (1 - z[c, m2]) - W * (1 - w[c, mm]))
            @constraint(m, pre[m2] >= pre[mm] - W * (1 - s[c]) - W * (1 - w[c, mm]))
        end
        for mm in 1:4; ℓ[mm] += q[c, mm]; end
    end
    @variable(m, sel[1:4], Bin)
    @constraint(m, sum(sel) == 1)
    if level < Inf
        for mm in 1:4; @constraint(m, ℓ[mm] >= level - 4.0 * (1 - sel[mm])); end
        set_objective_sense(m, MOI.FEASIBILITY_SENSE)
    else
        @variable(m, t)
        for mm in 1:4; @constraint(m, t <= ℓ[mm] + 4.0 * (1 - sel[mm])); end
        @objective(m, Max, t)
    end
    println("模型规模：变量 ", num_variables(m), "，约束 ", num_constraints(m; count_variable_in_set_constraints = false))
    t0 = time(); optimize!(m); el = time() - t0
    st = termination_status(m)
    if st == OPTIMAL
        if level < Inf
            println("可行 ⟹ 存在 ≥ ", level, " 的点")
        else
            println("松弛上界（整个家族） = ", round(objective_value(m), digits = 8))
            pv = value.(P)
            println("见证 p = ", round.(pv, digits = 5))
            cs = opt_makespan(pv, 4)
            println("该 p 的 C* = ", round(cs, digits = 5), "   A4c 负载 = ", round(a4_sim(pv, A4(C_TARGET, [:p1, :p45], false, false))[1], digits = 5),
                    "   真实比值 = ", round(a4_sim(pv, A4(C_TARGET, [:p1, :p45], false, false))[1] / cs, digits = 5))
            for c in 1:6
                println("   步 ", 4 + c, "  z = ", Int.(round.(value.(z[c, :]))), "  w = ", Int.(round.(value.(w[c, :]))), "  s = ", Int(round(value(s[c]))))
            end
        end
    else
        println("状态 = ", st, "（未在最优化意义上收敛）")
        st == INFEASIBLE && println("⟹ 不可行：不存在 ≥ ", level, " 的点（该块一次封闭）")
    end
    println("用时 ", round(el, digits = 1), " s")
end

function main()
    mode = ARGS[1]
    if mode == "level"
        reach_all(level = parse(Float64, ARGS[2]))
    else
        reach_all()
    end
end
main()
