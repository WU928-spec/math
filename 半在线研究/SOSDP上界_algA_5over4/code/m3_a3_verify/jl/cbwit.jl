include("a4_lib.jl"); include("a4_milp10.jl")
using JuMP, HiGHS
# 提取分支 B 最坏片的最优 p
function wit()
    for mm in 1:4
        n=10; m,P=_base(n; preds=:card); set_silent(m)
        ℓ = _trace!(m, P, [2,3,1,4,4,1], [14,12,9,8,8,0]; n=n, preds=:card)
        for m2 in 1:4; m2==mm && continue; @constraint(m, ℓ[mm] >= ℓ[m2]); end
        @objective(m, Max, ℓ[mm]); optimize!(m)
        if termination_status(m)==OPTIMAL
            pv = value.(P)
            println("最重机 $mm: 负载=", round(objective_value(m),digits=6), "  p=", round.(pv,digits=5))
        end
    end
end
wit()
