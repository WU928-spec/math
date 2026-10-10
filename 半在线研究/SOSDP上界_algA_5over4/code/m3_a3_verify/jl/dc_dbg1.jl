include("dc_coloc.jl")
n = 6; preds = :full45
m, P, q, c, empty = coloc_model(n, preds)
con = @constraint(m, c[n, 1] >= 1)
@objective(m, Max, 0.0 * P[1])
optimize!(m)
println("status = ", termination_status(m), "  primal = ", primal_status(m))
if primal_status(m) == FEASIBLE_POINT
    pv = value.(P)
    println("p = ", round.(pv, digits=6))
    println("τ = ", RHO * (pv[4] + pv[5]))
    for j in 5:n
        println(" step $j: c=", round.(value.(m[:c][j, :]), digits=3), " e=", round.(value.(m[:e][j, :]), digits=3),
                " empty=", round(value(empty[j]), digits=3),
                " yA=", round.(value.(m[:yA][j, :]), digits=4))
    end
    println("loads from model:")
    for j in 5:n
        for mm in 1:4
            lv = pv[mm] + sum(value(m[:yA][i, mm]) for i in 5:(j-1); init=0.0)
            print("  ℓ($j,$mm)=", round(lv, digits=5))
        end
        println()
    end
end
