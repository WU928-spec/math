# a4_razor_fixedu_milp.jl —— razor [2,2,2,3]：60 种机指派逐一带整装箱 MILP 求 sup(min+z)
#   目的：分解 razor 形状的 sup=1.2——找出哪些指派 razor-tight（=6/5，需精确证书），
#         哪些有大余量（浮点 MILP 即事实严谨）。接收机无关。
using JuMP, HiGHS

const PERMS3 = [[1,2,3],[1,3,2],[2,1,3],[2,3,1],[3,1,2],[3,2,1]]

function milp_sup(assign)
    n = 10
    m = Model(HiGHS.Optimizer); set_silent(m); set_time_limit_sec(m, 60.0)
    @variable(m, 4 / 15 <= P[1:n] <= 1.0)
    for i in 1:(n-1); @constraint(m, P[i] >= P[i+1]); end
    @constraint(m, sum(P) <= 4.0)
    @constraint(m, P[n] <= 1 / 3)
    # 固定机指派：负载为显式线性形
    ℓ = [sum(P[i] for i in assign[mm]) for mm in 1:4]
    # 装箱（整数）
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
    termination_status(m) == OPTIMAL || return NaN, Float64[]
    return objective_value(m), value.(P)
end

function main()
    tight = Any[]
    worst = -Inf
    for a in 5:9, b in (a+1):9
        rest = setdiff(5:9, [a, b])
        for pm in PERMS3
            assign = [[1, rest[pm[1]]], [2, rest[pm[2]]], [3, rest[pm[3]]], [4, a, b]]
            v, pv = milp_sup(assign)
            isnan(v) && (println("  TIMEOUT/异常 $assign"); continue)
            v > worst && (worst = v)
            if v > 1.2 - 0.005          # razor-tight（余量 < 0.005）的指派单列
                push!(tight, (round(v, digits = 6), assign, round.(pv, digits = 4)))
            end
        end
    end
    println("60 种指派最大 sup = $worst")
    println("razor-tight（sup > 1.195）指派数 = $(length(tight))：")
    for (v, a, pv) in sort(tight; by = x -> -x[1])
        println("  sup=$v  assign=$a  p=$pv")
    end
end

main()
