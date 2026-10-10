# a4_razor_relax.jl —— razor 形状 [2,2,2,3] + H 的 LP 松弛 sup 测试
#   关键：固定形状下 "min+z > 6/5" ⟺ H（四机负载全 > 6/5−z）。
#   若 LP 松弛（机指派/装箱分数化）的 sup ≤ 6/5，则精确有理对偶 = 严谨证书。
#   纯 LP，几秒出结果。
using JuMP, HiGHS

function razor_relax(; integer_x = false, add_struct = true)
    n = 10
    m = Model(HiGHS.Optimizer); set_silent(m)
    @variable(m, 4 / 15 <= P[1:n] <= 1.0)
    for i in 1:(n-1); @constraint(m, P[i] >= P[i+1]); end
    @constraint(m, sum(P) <= 4.0)
    @constraint(m, P[n] <= 1 / 3)
    # 机指派 u（连续松弛）
    @variable(m, 0 <= u[1:(n-1), 1:4] <= 1)
    @variable(m, v[1:(n-1), 1:4] >= 0)
    for i in 1:(n-1)
        @constraint(m, sum(u[i, :]) == 1)
        for mm in 1:4
            @constraint(m, v[i, mm] <= u[i, mm])
            @constraint(m, v[i, mm] <= P[i])
            @constraint(m, v[i, mm] >= P[i] - (1 - u[i, mm]))
        end
    end
    cnt = [2, 2, 2, 3]
    for mm in 1:4
        @constraint(m, u[mm, mm] == 1)
        @constraint(m, sum(u[:, mm]) == cnt[mm])
    end
    ℓ = [sum(v[:, mm]) for mm in 1:4]
    # 装箱 x（可选整数/连续）
    if integer_x
        @variable(m, x[1:n, 1:4], Bin)
    else
        @variable(m, 0 <= x[1:n, 1:4] <= 1)
    end
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
    if add_struct
        @constraint(m, P[4] + P[5] >= P[1])          # Λ = p4+p5 分支（H 下已证）
        @constraint(m, P[n] >= 11 / 40)              # razor 存活 z 窗口下界（§3e 补遗二）
    end
    # H：四机负载全 > 6/5 − z（求 sup 时用 t 逼近；这里直接查 6/5+ε 的可行性）
    @variable(m, t)
    for mm in 1:4; @constraint(m, t <= ℓ[mm] + P[n]); end
    @objective(m, Max, t)
    optimize!(m)
    return objective_value(m), termination_status(m)
end

for (ix, st) in ((false, false), (false, true), (true, true))
    v, status = razor_relax(; integer_x = ix, add_struct = st)
    println("integer_x=$ix  add_struct=$st   sup(min+z) = ", isnan(v) ? status : round(v, digits = 8))
    flush(stdout)
end
