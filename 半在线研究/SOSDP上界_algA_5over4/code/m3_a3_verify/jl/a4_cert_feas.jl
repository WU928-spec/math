# a4_cert_feas.jl —— 层(5)/层(3) 证书化可行性探针
#   模式 1：层 (5) 终端 MILP 的 LP 松弛（u,x 连续）sup 是否 < 6/5？
#   模式 2：层 (3) 逐片「轨迹约束（线性）+ 合法装箱割（无二元）」LP 的 sup 分布
using JuMP, HiGHS

function layer5_relax(cnt)
    n = 11
    m = Model(HiGHS.Optimizer); set_silent(m)
    @variable(m, 4 / 15 <= P[1:n] <= 1.0)
    for i in 1:(n-1); @constraint(m, P[i] >= P[i+1]); end
    @constraint(m, sum(P) <= 4.0)
    @constraint(m, P[n] <= 1 / 3)
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
    for mm in 1:4
        @constraint(m, u[mm, mm] == 1)
        @constraint(m, sum(u[:, mm]) == cnt[mm])
    end
    ℓ = [sum(v[:, mm]) for mm in 1:4]
    @variable(m, 0 <= x[1:n, 1:4] <= 1)
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

function mode1()
    println("== 层 (5) 终端 LP 松弛（u,x 全连续；真 MILP sup=7/6）==")
    for a in 1:4, b in (a+1):4
        c = fill(2, 4); c[a] = 3; c[b] = 3
        v = layer5_relax(c)
        println("  cnt=$c : sup = ", isnan(v) ? "NaN" : round(v, digits = 6))
    end
end

mode1()
