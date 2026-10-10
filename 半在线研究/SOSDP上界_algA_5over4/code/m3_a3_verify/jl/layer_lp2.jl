# layer_lp2.jl —— 开放区间版层封顶：julia --project=. layer_lp2.jl <layer> <zmin> <zmax>
using JuMP, HiGHS

function layer_ceiling(n, cnt, zmin, zcap; tlim = 90.0)
    m = Model(HiGHS.Optimizer); set_silent(m); set_time_limit_sec(m, tlim)
    @variable(m, P[1:n])
    for i in 1:n; set_lower_bound(P[i], 4 / 15); set_upper_bound(P[i], 1.0); end
    for i in 1:(n-1); @constraint(m, P[i] >= P[i+1]); end
    @constraint(m, sum(P) <= 4.0)
    @constraint(m, P[n] <= zcap); @constraint(m, P[n] >= zmin)
    @variable(m, u[1:(n-1), 1:4], Bin); @variable(m, v[1:(n-1), 1:4] >= 0)
    for i in 1:(n-1)
        @constraint(m, sum(u[i, :]) == 1)
        for mm in 1:4
            @constraint(m, v[i, mm] <= u[i, mm]); @constraint(m, v[i, mm] <= P[i])
            @constraint(m, v[i, mm] >= P[i] - (1 - u[i, mm]))
        end
    end
    for mm in 1:4
        @constraint(m, u[mm, mm] == 1); @constraint(m, sum(u[:, mm]) == cnt[mm])
    end
    ℓ = [sum(v[:, mm]) for mm in 1:4]
    @variable(m, x[1:n, 1:4], Bin); @variable(m, y[1:n, 1:4] >= 0)
    for i in 1:n
        @constraint(m, sum(x[i, :]) == 1)
        for b in 1:4
            @constraint(m, y[i, b] <= x[i, b]); @constraint(m, y[i, b] <= P[i])
            @constraint(m, y[i, b] >= P[i] - (1 - x[i, b]))
        end
    end
    for b in 1:4
        @constraint(m, sum(y[:, b]) <= 1.0); @constraint(m, sum(x[:, b]) <= 3)
    end
    @constraint(m, x[1, 1] == 1)
    @variable(m, t)
    for mm in 1:4; @constraint(m, t <= ℓ[mm] + P[n]); end
    @objective(m, Max, t)
    optimize!(m)
    return termination_status(m) == OPTIMAL ? (objective_value(m), value.(P)) :
           (primal_status(m) == FEASIBLE_POINT ? (objective_value(m), value.(P)) : (NaN, Float64[]))
end

function main()
    which = ARGS[1]; zmin = parse(Float64, ARGS[2]); zmax = parse(Float64, ARGS[3])
    cfgs = Dict(
        "1" => (8, [[2,2,2,1],[2,2,1,2],[2,1,2,2],[1,2,2,2]]),
        "2" => (9, [[c...] for c in ([[ifelse(i==a,3,ifelse(i==b,1,2)) for i in 1:4] for a in 1:4 for b in 1:4 if a!=b])]),
        "3" => (9, [[2,2,2,2]]),
        "5" => (11, [[ifelse(i==a||i==b,3,2) for i in 1:4] for a in 1:4 for b in (a+1):4]),
    )
    (n, cnts) = cfgs[which]
    for cnt in cnts
        v, pv = layer_ceiling(n, cnt, zmin, zmax)
        println("层($which) cnt=$cnt z∈[$zmin,$zmax]: sup = ", isnan(v) ? "不可行" : round(v, digits = 6),
                isnan(v) ? "" : "  见证=" * join(round.(pv, digits = 4), " "))
        flush(stdout)
    end
end
main()
