# a4_l3_seg.jl —— 层 (3) 硬段测试：H + Λ=p45 > 6/5−z+ε 是否可行？
#   不可行 ⟹ H ⟹ Λ ≤ 6/5−z ⟹ min ≤ Λ ≤ 6/5−z（min≤Λ 引理已在案）⟹ 层 (3) 闭合。
#   用法：julia a4_l3_seg.jl [ε]
using JuMP, HiGHS

function test(ε)
    n = 9
    m = Model(HiGHS.Optimizer); set_silent(m); set_time_limit_sec(m, 120.0)
    @variable(m, 4 / 15 <= P[1:n] <= 1.0)
    for i in 1:(n-1); @constraint(m, P[i] >= P[i+1]); end
    @constraint(m, sum(P) <= 4.0)
    # 机指派（{2,2,2,2}：每台恰收一件）
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
        @constraint(m, sum(u[:, mm]) == 2)
    end
    ℓ = [sum(v[:, mm]) for mm in 1:4]
    for mm in 1:4; @constraint(m, ℓ[mm] >= 6 / 5 - P[n]); end   # H
    # Λ = p45 分支 + 硬段条件
    @constraint(m, P[4] + P[5] >= P[1])
    @constraint(m, P[4] + P[5] >= 6 / 5 - P[n] + ε)
    # 装箱
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
    @objective(m, Max, P[4] + P[5])
    optimize!(m)
    return termination_status(m), (termination_status(m) == OPTIMAL ? objective_value(m) : NaN)
end

for ε in (0.0, 0.001)
    st, v = test(ε)
    println("ε=$ε : 状态=$st  max Λ=", isnan(v) ? "—" : round(v, digits = 6))
    flush(stdout)
end
