# a4_landscape.jl —— 全形状终态封顶地图（绕开引理 B 的计算确认）
#   对所有 n=6..12、所有有序计数向量 cnt（4 台、每台 1..3 件、和=n-1，初始件绑定 u[mm,mm]=1）
#   求终态松弛 sup(min_pre + z)（装箱二元自适应、Σp≤4、秩序、P∈[4/15,1]、z≤1/3）。
#   接收机无关 ⟹ 覆盖"接收机 3 件"的全部变体；sup ≤ 6/5 的形状无需任何手证。
#   用法：julia --project=. a4_landscape.jl <n>   （每个 n 一次运行，守 8 分钟纪律）
using JuMP, HiGHS

function layer_ceiling(n, cnt, zcap; tlim = 90.0)
    m = Model(HiGHS.Optimizer); set_silent(m); set_time_limit_sec(m, tlim)
    @variable(m, P[1:n])
    for i in 1:n; set_lower_bound(P[i], 4 / 15); set_upper_bound(P[i], 1.0); end
    for i in 1:(n-1); @constraint(m, P[i] >= P[i+1]); end
    @constraint(m, sum(P) <= 4.0)
    @constraint(m, P[n] <= zcap)
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
    st = termination_status(m)
    if st == OPTIMAL
        return objective_value(m), value.(P), "OPT"
    elseif primal_status(m) == FEASIBLE_POINT
        return objective_value(m), value.(P), "TIMELIMIT(下界)"
    else
        return NaN, Float64[], string(st)
    end
end

"有序计数向量：4 台、每台 1..3、和 = n-1"
function count_vectors(n)
    out = Vector{Int}[]
    for c1 in 1:3, c2 in 1:3, c3 in 1:3, c4 in 1:3
        c1 + c2 + c3 + c4 == n - 1 && push!(out, [c1, c2, c3, c4])
    end
    return out
end

function main()
    n = parse(Int, ARGS[1])
    cvs = count_vectors(n)
    println("n=$(n)：", length(cvs), " 个有序计数形状")
    results = Tuple{Float64, Vector{Int}, String}[]
    for cnt in cvs
        v, _, st = layer_ceiling(n, cnt, 1 / 3)
        push!(results, (v, cnt, st))
        println("  cnt=$cnt : ", isnan(v) ? st : round(v, digits = 6))
        flush(stdout)
    end
    println("\n=== n=$n 汇总（按 sup 降序）===")
    sort!(results; by = r -> isnan(r[1]) ? -Inf : r[1], rev = true)
    for (v, cnt, st) in results
        flag = isnan(v) ? "?" : (v > 1.2 + 1e-9 ? "✗ 超 6/5" : (v > 1.2 - 1e-9 ? "=razor" : "✓"))
        println("  ", isnan(v) ? st : round(v, digits = 6), "  cnt=$cnt  $flag")
    end
end

main()
