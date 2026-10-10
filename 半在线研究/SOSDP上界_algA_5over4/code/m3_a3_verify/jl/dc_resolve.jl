# dc_resolve.jl —— 对待定对逐一判定：relaxed（任何 tie-break 超集，不可行=严格 NEVER）
#   与 exact(ε)（真实 tie-break，可行+模拟复核=严格 WITNESS）
include("dc_coloc.jl")

function decide(preds, n, i; tlim = 600.0)
    println("### ($i,$n) @ $preds")
    for (sem, eps) in ((:relaxed, 0.0), (:exact, 1e-3), (:exact, 1e-4))
        m, P, q, c, empty = coloc_model(n, preds; semantics = sem, eps = eps)
        set_time_limit_sec(m, tlim)
        con = i <= 4 ? @constraint(m, c[n, i] >= 1) : @constraint(m, q[i] >= 1)
        @objective(m, Max, 0.0 * P[1])
        t0 = time(); optimize!(m)
        st = termination_status(m); el = round(time() - t0, digits = 1)
        if st == INFEASIBLE || st == INFEASIBLE_OR_UNBOUNDED
            tag = sem == :relaxed ? "NEVER(严格, 任意 tie-break)" : "NEVER*(ε=$eps)"
            println("   $sem eps=$eps: $tag  [$(el)s]"); flush(stdout)
            return :never
        elseif primal_status(m) == FEASIBLE_POINT
            pv = value.(P)
            ok = sim_coloc(pv, i)
            println("   $sem eps=$eps: FEASIBLE sim=$ok  p=", join(round.(pv, digits=5), " "), "  [$(el)s]")
            flush(stdout)
            ok && return :witness
        else
            println("   $sem eps=$eps: $st  [$(el)s]"); flush(stdout)
            return :unknown
        end
    end
    return :unknown
end

function main()
    tlim = length(ARGS) >= 1 ? parse(Float64, ARGS[1]) : 600.0
    for (preds, n, i) in ((:full1, 11, 8), (:full1, 11, 4),
                          (:full45, 12, 9), (:full45, 12, 10), (:full45, 12, 11),
                          (:full1, 11, 9), (:full1, 11, 10),
                          (:full45, 6, 5), (:full45, 7, 5), (:full45, 8, 5), (:full1, 5, 1))
        decide(preds, n, i; tlim = tlim)
    end
end
main()
