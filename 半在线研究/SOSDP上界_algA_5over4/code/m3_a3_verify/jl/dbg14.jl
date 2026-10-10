using JuMP, HiGHS
m = Model(HiGHS.Optimizer); set_silent(m)
@variable(m, P[1:6]); for i in 1:6; fix(P[i], 0.5, force=true); end
ρ = 1.18
τ = ρ * (P[4] + P[5])
ℓ = [AffExpr(0.0) for _ in 1:4]
for mm in 1:4; ℓ[mm] += P[mm]; end
E5 = [2,3,4]; a5 = 2
pre = copy(ℓ)
for mm in 1:4
    mm in E5 ? @constraint(m, pre[mm] + P[5] <= τ) : @constraint(m, pre[mm] + P[5] >= τ)
end
for mm in E5; mm == a5 && continue; @constraint(m, pre[a5] >= pre[mm]); end
n = 0
for c in all_constraints(m; include_variable_in_set_constraints = false)
    global n += 1; println(n, ": ", c)
end
