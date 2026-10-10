include("dc_dff.jl")
function case_10_wit(n, i, ms, preds, layer)
    m, P = failure_model(n, preds, layer)
    τ = τof(P, preds)
    S = sum(P[k] for k in 1:(n-1))
    L = P[ms] + P[i]
    @constraint(m, L <= τ)
    @constraint(m, L <= S / 4)
    @constraint(m, S >= L + 3 * (τ - P[n]))
    @objective(m, Max, L + P[n])
    optimize!(m)
    return termination_status(m) == OPTIMAL ? (objective_value(m), value.(P)) : (NaN, Float64[])
end
function case_01_wit(n, jp, ms, preds, layer)
    m, P = failure_model(n, preds, layer)
    τ = τof(P, preds)
    Sp = sum(P[k] for k in 1:(jp-1))
    L = P[ms] + P[jp]
    @constraint(m, Sp >= P[ms] + 3 * (τ - P[jp]))
    @constraint(m, P[ms] <= Sp / 4)
    S = sum(P[k] for k in 1:(n-1))
    @constraint(m, L <= S / 4)
    @constraint(m, S >= L + 3 * (τ - P[n]))
    @objective(m, Max, L + P[n])
    optimize!(m)
    return termination_status(m) == OPTIMAL ? (objective_value(m), value.(P)) : (NaN, Float64[])
end
function main()
    best = -Inf; bp = Float64[]; bi = 0; bms = 0
    for ms in 1:4, i in 5:9
        v, pv = case_10_wit(10, i, ms, :full45, 2)
        if !isnan(v) && v > best; best = v; bp = pv; bi = i; bms = ms; end
    end
    println("(1,0) L2 天花板 = ", round(best, digits=6), "  i=$bi ms=$bms")
    println("见证 p = ", round.(bp, digits=4))
    println("C*(p) = ", round(opt_makespan(bp, 4), digits=6), "  可装箱(C*≤1)? ", opt_makespan(bp, 4) <= 1 + 1e-9)
    best = -Inf; bp = Float64[]; bjp = 0; bms = 0
    for ms in 1:4, jp in 5:9
        v, pv = case_01_wit(10, jp, ms, :full45, 2)
        if !isnan(v) && v > best; best = v; bp = pv; bjp = jp; bms = ms; end
    end
    println("(0,1) L2 天花板 = ", round(best, digits=6), "  jp=$bjp ms=$bms")
    println("见证 p = ", round.(bp, digits=4))
    println("C*(p) = ", round(opt_makespan(bp, 4), digits=6), "  可装箱(C*≤1)? ", opt_makespan(bp, 4) <= 1 + 1e-9)
end
main()
