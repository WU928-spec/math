include("a4_lib.jl")
p = [0.68333, 0.36667, 0.36667, 0.36667, 0.31667, 0.31667, 0.31667, 0.31667, 0.31667, 0.31667, 0.26667]
cs = opt_makespan(p, 4); println("C* = ", cs)
pn = p ./ cs
ms, asg, load = a4_sim(pn, A4(C_TARGET, [:p1, :p45], false, false))
println("asg = ", asg)
println("loads = ", round.(load, digits=5), "  makespan = ", round(ms, digits=5))
println("(4,11) co-located: ", any(mm -> 4 in asg[mm] && 11 in asg[mm], 1:4))
println("(8,11) co-located: ", any(mm -> 8 in asg[mm] && 11 in asg[mm], 1:4))
println("(9,11) co-located: ", any(mm -> 9 in asg[mm] && 11 in asg[mm], 1:4))
println("(10,11) co-located: ", any(mm -> 10 in asg[mm] && 11 in asg[mm], 1:4))
# 逐步重放
τ = C_TARGET * max(pn[1], pn[4] + pn[5])
ld = zeros(4)
for j in 1:4; ld[j] += pn[j]; end
println("τ = ", round(τ, digits=6))
for j in 5:11
    E = [mm for mm in 1:4 if ld[mm] + pn[j] <= τ + 1e-15]
    aj = isempty(E) ? argmin(ld) : E[argmax(ld[E])]
    println("  step $j: p=$(round(pn[j],digits=4)) E=$E → M$aj   loads=", round.(ld, digits=4))
    ld[aj] += pn[j]
end
