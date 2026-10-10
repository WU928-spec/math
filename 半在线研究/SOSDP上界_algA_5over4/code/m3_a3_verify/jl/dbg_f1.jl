include("a4_lib.jl"); include("a4_milp10.jl")
# 直接测 full1 预言机在已知可行片上
for (k, ms) in [([2],[14]), ([3],[14]), ([2],[7]), ([1],[15])]
    r = piece_feasible(k, ms; preds = :full1)
    println("k=", k, " masks=", ms, "  full1 可行? ", r)
end
# 手工复核实例
p = [0.9,0.3,0.3,0.3,0.3]
println("opt_makespan = ", opt_makespan(p,4), "  (应为 0.9)")
τ = C_TARGET * p[1]; println("τ = ", τ)
println("E5 = ", [m for m in 1:4 if (m<=4 ? p[m] : 0.0) + p[5] <= τ])
