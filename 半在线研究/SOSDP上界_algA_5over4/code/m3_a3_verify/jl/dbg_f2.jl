include("a4_lib.jl"); include("a4_milp10.jl")
using JuMP, HiGHS
n = 5
m, P = _base(n; preds = :full1, cuts = false)
pv = [0.9,0.3,0.3,0.3,0.3]
for i in 1:n; fix(P[i], pv[i], force=true); end
ℓ = _trace!(m, P, [2], [14]; n = n, preds = :full1)
@objective(m, Min, 0*P[1]); optimize!(m)
println("状态 = ", termination_status(m))
for c in all_constraints(m; include_variable_in_set_constraints = false)
    ok = is_valid(m, c)
    ok || println("违反: ", c)
end
