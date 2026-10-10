# a4_Htest_gen.jl —— 通用 H-可行性测试：形状(n, cnt) + H（四机负载 ≥ 6/5−z）下 z 的最大值
#   判读：max z 不可行 ⟹ H 空 ⟹ 该层纯终态闭合（无需轨迹）；
#         max z = z₀ 可行 ⟹ H 可行 ⟹ 该层需轨迹/证书（z₀ 即失败窗口的右端）。
#   用法：julia --project=. a4_Htest_gen.jl <n> <c1,c2,c3,c4> [δ]
using JuMP, HiGHS

function maxz_under_H(n, cnt, δ)
    m = Model(HiGHS.Optimizer); set_silent(m); set_time_limit_sec(m, 90.0)
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
    for mm in 1:4; @constraint(m, ℓ[mm] >= 6 / 5 - P[n] - δ); end   # H（放宽 δ）
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
    termination_status(m) == OPTIMAL || return NaN, Float64[]
    return objective_value(m), value.(P)
end

function main()
    n = parse(Int, ARGS[1])
    cnt = parse.(Int, split(ARGS[2], ","))
    δ = length(ARGS) >= 3 ? parse(Float64, ARGS[3]) : 0.0
    v, pv = maxz_under_H(n, cnt, δ)
    if isnan(v)
        println("n=$n cnt=$cnt δ=$δ : H 不可行（⟹ 该形状纯终态闭合）")
    else
        println("n=$n cnt=$cnt δ=$δ : H 可行，最大 z = $(round(v, digits=6))，见证 p=$(join(round.(pv, digits=4), " "))")
    end
end

main()
