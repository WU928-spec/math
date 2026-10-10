# layer_lp.jl —— 5 个开放层的"终态松弛"封顶测试
#   对每层（n, 机计数, 箱划分由装箱二元自适应）：max ℓ_min + z
#   约束：秩序、P∈[4/15,1]、Σp≤4、装箱（4箱≤3件≤1）、机计数（初始件绑定机 m 含 p_m）、
#         z 由兜底（隐含 n≥6）、z ≤ 1/3（已证）、层(1)(2) 加 z ≤ 3/10。
#   sup < 6/5 ⟹ 终态封死；= 6/5 ⟹ razor；> 6/5 ⟹ 必须轨迹。
using JuMP, HiGHS

"单层封顶：n、计数向量 cnt（长度4，和=n-1）、zcap。返回 (sup, 见证 P)"
function layer_ceiling(n, cnt, zcap; tlim = 120.0)
    m = Model(HiGHS.Optimizer); set_silent(m); set_time_limit_sec(m, tlim)
    @variable(m, P[1:n])
    for i in 1:n; set_lower_bound(P[i], 4 / 15); set_upper_bound(P[i], 1.0); end
    for i in 1:(n-1); @constraint(m, P[i] >= P[i+1]); end
    @constraint(m, sum(P) <= 4.0)
    @constraint(m, P[n] <= zcap)
    # 机分配 u[i,mm]（i ≤ n-1）；初始件绑定 u[m,m]=1；计数
    @variable(m, u[1:(n-1), 1:4], Bin)
    @variable(m, v[1:(n-1), 1:4] >= 0)
    for i in 1:(n-1)
        @constraint(m, sum(u[i, :]) == 1)
        for mm in 1:4
            @constraint(m, v[i, mm] <= u[i, mm])
            @constraint(m, v[i, mm] <= P[i])
            @constraint(m, v[i, mm] >= P[i] - (1 - u[i, mm]))
        end
    end
    for mm in 1:4
        @constraint(m, u[mm, mm] == 1)
        @constraint(m, sum(u[:, mm]) == cnt[mm])
    end
    ℓ = [sum(v[:, mm]) for mm in 1:4]
    # 装箱 x[i,b]（全体 n 件含 z）
    @variable(m, x[1:n, 1:4], Bin)
    @variable(m, y[1:n, 1:4] >= 0)
    for i in 1:n
        @constraint(m, sum(x[i, :]) == 1)
        for b in 1:4
            @constraint(m, y[i, b] <= x[i, b])
            @constraint(m, y[i, b] <= P[i])
            @constraint(m, y[i, b] >= P[i] - (1 - x[i, b]))
        end
    end
    for b in 1:4
        @constraint(m, sum(y[:, b]) <= 1.0)
        @constraint(m, sum(x[:, b]) <= 3)
    end
    @constraint(m, x[1, 1] == 1)
    # 目标：max ℓ_min + z
    @variable(m, t)
    for mm in 1:4; @constraint(m, t <= ℓ[mm] + P[n]); end
    @objective(m, Max, t)
    optimize!(m)
    st = termination_status(m)
    if st == OPTIMAL
        return objective_value(m), value.(P)
    elseif primal_status(m) == FEASIBLE_POINT
        return objective_value(m), value.(P)   # 超时但有可行点：下界
    else
        return NaN, Float64[]
    end
end

function run_layer(name, n, cnts, zcap)
    best = -Inf; bp = Float64[]
    for cnt in cnts
        v, pv = layer_ceiling(n, cnt, zcap)
        if !isnan(v) && v > best; best = v; bp = pv; end
        println("  $name cnt=$cnt : sup ℓ_min+z = ", isnan(v) ? "不可行" : round(v, digits = 6))
        flush(stdout)
    end
    println("层 $name 总 sup = ", round(best, digits = 6),
            best > 0 ? "  见证=" * join(round.(bp, digits = 4), " ") : "")
    return best
end

function main()
    # 层 (1)：n=8 {2,2,2,1}，z≤0.3；选 1-lump 机
    run_layer("(1) n8", 8, [[2,2,2,1],[2,2,1,2],[2,1,2,2],[1,2,2,2]], 0.3)
    # 层 (2)：n=9 {3,2,2,1}，z≤0.3；选 3-lump 与 1-lump 机
    c2 = []
    for a in 1:4, b in 1:4
        a == b && continue
        c = fill(2, 4); c[a] = 3; c[b] = 1; push!(c2, c)
    end
    run_layer("(2) n9", 9, c2, 0.3)
    # 层 (3)：n=9 {2,2,2,2}，z≤1/3
    run_layer("(3) n9", 9, [[2,2,2,2]], 1 / 3)
    # 层 (4)：n=10 {3,2,2,2}，z≤1/3；选 3-lump 机
    c4 = []
    for a in 1:4; c = fill(2, 4); c[a] = 3; push!(c4, c); end
    run_layer("(4) n10", 10, c4, 1 / 3)
    # 层 (5)：n=11 {3,3,2,2}，z≤1/3；选两台 3-lump 机
    c5 = []
    for a in 1:4, b in (a+1):4
        c = fill(2, 4); c[a] = 3; c[b] = 3; push!(c5, c)
    end
    run_layer("(5) n11", 11, c5, 1 / 3)
end
main()
