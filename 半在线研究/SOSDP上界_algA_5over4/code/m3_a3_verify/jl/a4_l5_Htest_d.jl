# a4_l5_Htest.jl —— 层 (5) 关键检验：形状 + H（四机负载 ≥ 6/5−z）下 z 的最大值
#   若 max z ≤ 4/15（边界），则 H 在开区间 (4/15, 1/3] 不可行 ⟹ 层 (5) 纯终态闭合，无需轨迹。
using JuMP, HiGHS

function maxz_under_H(cnt)
    n = 11
    m = Model(HiGHS.Optimizer); set_silent(m)
    @variable(m, 4 / 15 <= P[1:n] <= 1.0)
    for i in 1:(n-1); @constraint(m, P[i] >= P[i+1]); end
    @constraint(m, sum(P) <= 4.0)
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
    for mm in 1:4; @constraint(m, ℓ[mm] >= 6 / 5 - P[n] - 0.005); end   # H
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
    @objective(m, Max, P[n])
    optimize!(m)
    if termination_status(m) == OPTIMAL
        return objective_value(m), value.(P)
    else
        return NaN, Float64[]
    end
end

for a in 1:4, b in (a+1):4
    c = fill(2, 4); c[a] = 3; c[b] = 3
    v, pv = maxz_under_H(c)
    println("cnt=$c : max z | H-δ= ", isnan(v) ? "不可行" : round(v, digits = 6),
            isnan(v) ? "" : "  p=" * join(round.(pv, digits = 4), " "))
    flush(stdout)
end
