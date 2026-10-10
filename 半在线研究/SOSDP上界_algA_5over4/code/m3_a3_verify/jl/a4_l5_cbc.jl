# a4_l5_cbc.jl —— 层 (5) 终端 sup 的 CBC 交叉验证（与 HiGHS 结果 7/6 对照）
using JuMP, Cbc

function layer5_ceiling_cbc(cnt)
    n = 11
    m = Model(Cbc.Optimizer); set_silent(m)
    @variable(m, 4 / 15 <= P[1:n] <= 1.0)
    for i in 1:(n-1); @constraint(m, P[i] >= P[i+1]); end
    @constraint(m, sum(P) <= 4.0)
    @constraint(m, P[n] <= 1 / 3)
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
    @variable(m, t)
    for mm in 1:4; @constraint(m, t <= ℓ[mm] + P[n]); end
    @objective(m, Max, t)
    optimize!(m)
    return termination_status(m) == OPTIMAL ? objective_value(m) : NaN
end

for a in 1:4, b in (a+1):4
    c = fill(2, 4); c[a] = 3; c[b] = 3
    v = layer5_ceiling_cbc(c)
    println("CBC  cnt=$c : sup = ", isnan(v) ? "NaN" : round(v, digits = 6))
    flush(stdout)
end
