include("common.jl")
using JuMP, HiGHS
const RHO = C_TARGET
p = [0.6,0.5,0.5,0.4,0.4,0.4,0.3,0.3,0.3,0.3]
k = [2,3,1,4,1,2]; masks = [14,12,9,8,0,0]
# 手工复核算法轨迹
load = zeros(4); for j in 1:4; load[j] = p[j]; end
τ = RHO*(p[4]+p[5]); println("τ = ", τ)
for c in 1:6
    j = 4+c; Ej = [m for m in 1:4 if (masks[c] >> (m-1)) & 1 == 1]
    println("j=", j, "  p_j=", p[j], "  E=", Ej, "  load=", round.(load,digits=4),
            "  argmax判定 a=", k[c])
    for m in 1:4
        ok = (m in Ej) ? (load[m]+p[j] <= τ + 1e-12) : (load[m]+p[j] >= τ - 1e-12)
        ok || println("   ✗ m=", m, " 违反：load+p=j = ", load[m]+p[j])
    end
    load[k[c]] += p[j]
end
println("末态 load = ", round.(load, digits=4))
