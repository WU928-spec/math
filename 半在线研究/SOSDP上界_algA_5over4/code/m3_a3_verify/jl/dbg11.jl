include("common.jl")
using JuMP, HiGHS
const RHO = C_TARGET
const NT = 10
p = [0.6,0.5,0.5,0.4,0.4,0.4,0.3,0.3,0.3,0.3]
k = [2,3,1,4,1,2]; masks = [14,12,9,8,0,0]
# 已知可行装箱
bins = [[1,5],[2,3],[4,7,8],[6,9,10]]
m = Model(HiGHS.Optimizer); set_silent(m)
@variable(m, P[1:NT])
for i in 1:NT; fix(P[i], p[i], force=true); end
for i in 1:(NT-1); @constraint(m, P[i] >= P[i+1]); end
@constraint(m, P[4]+P[5] >= P[1]); @constraint(m, P[2] <= P[3]+P[4])
@constraint(m, P[3] <= P[4]+P[5]); @constraint(m, P[5] <= P[3])
@constraint(m, sum(P) <= 4.0)
@variable(m, x[1:NT,1:4], Bin); @variable(m, y[1:NT,1:4])
for i in 1:NT, b in 1:4; fix(y[i,b], (i in bins[b]) ? p[i] : 0.0, force=true); end
for i in 1:NT
    @constraint(m, sum(x[i,:]) == 1)
    for b in 1:4
        @constraint(m, y[i,b] <= x[i,b]); @constraint(m, y[i,b] <= P[i])
        @constraint(m, y[i,b] >= P[i]-(1-x[i,b])); @constraint(m, y[i,b] >= 0)
    end
end
for b in 1:4
    @constraint(m, sum(y[i,b] for i in 1:NT) <= 1.0)
    @constraint(m, sum(x[i,b] for i in 1:NT) <= 3)
end
@constraint(m, x[1,1] == 1); @constraint(m, x[5,1] == 1)
for b in 2:4, i in bins[b]; @constraint(m, x[i,b] == 1); end
τ = RHO*(P[4]+P[5])
ℓ = [AffExpr(0.0) for _ in 1:4]; for mm in 1:4; ℓ[mm] += P[mm]; end
for c in 1:6
    j = 4+c; Ej = [mm for mm in 1:4 if (masks[c] >> (mm-1)) & 1 == 1]; aj = k[c]
    pre = copy(ℓ)
    for mm in 1:4
        mm in Ej ? @constraint(m, pre[mm]+P[j] <= τ) : @constraint(m, pre[mm]+P[j] >= τ)
    end
    if isempty(Ej); for mm in 1:4; @constraint(m, pre[aj] <= pre[mm]); end
    else; for mm in Ej; @constraint(m, pre[aj] >= pre[mm]); end; end
    ℓ[aj] += P[j]
end
@variable(m, t); for mm in 1:4; @constraint(m, t <= ℓ[mm]); end
@objective(m, Max, t)
optimize!(m)
println("约束总数 = ", num_constraints(m; count_variable_in_set_constraints=false))
for (i, con) in enumerate(all_constraints(m; include_variable_in_set_constraints = false))
    i > 100000 && break
    println(i, ": ", con)
end
println("状态 = ", termination_status(m))
