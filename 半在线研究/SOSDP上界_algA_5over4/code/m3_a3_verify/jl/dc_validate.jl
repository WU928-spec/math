# dc_validate.jl —— 校验 :exact 模型：凡所有判定余量 ≥ ε 的真实实例，模型必须可行
include("dc_coloc.jl")
using Random

const EPS = 1e-3

function rand_fam(n::Int, preds::Symbol, rng)
    while true
        p = gen_instance(n, rng; lower = ALP + 1e-9,
                         family = rand(rng, (:pow, :blocks, :two, :tight, :general)))
        cs = opt_makespan(p, 4); pn = p ./ cs
        minimum(pn) < ALP - 1e-9 && continue
        preds == :full1 && !(pn[1] >= pn[4] + pn[5] - 1e-12) && continue
        preds == :full45 && !(pn[4] + pn[5] >= pn[1] - 1e-12) && continue
        return pn
    end
end

"真实轨迹的所有判定余量；返回最小余量（E 判定与 argmax/argmin 间隔）"
function min_margin(p)
    n = length(p); τ = C_TARGET * max(p[1], p[4] + p[5])
    load = zeros(4); mg = Inf
    for j in 1:4; load[j] += p[j]; end
    for j in 5:n
        slack = [load[mm] + p[j] - τ for mm in 1:4]
        mg = min(mg, minimum(abs.(slack)))
        E = [mm for mm in 1:4 if slack[mm] <= 0]
        if isempty(E)
            aj = argmin(load)
            vals = sort(load)
            mg = min(mg, vals[2] - vals[1])
        else
            aj = E[argmax(load[E])]
            vals = sort(load[E]; rev = true)
            length(vals) >= 2 && (mg = min(mg, vals[1] - vals[2]))
        end
        load[aj] += p[j]
    end
    return mg
end

function main()
    rng = MersenneTwister(11)
    ntest = 0; nbad = 0; nskip = 0
    for preds in (:full45, :full1), n in (6, 9, 11)
        for t in 1:20
            p = rand_fam(n, preds, rng)
            mg = min_margin(p)
            if mg < EPS
                nskip += 1; continue
            end
            ntest += 1
            m, P, q, c, empty = coloc_model(n, preds; semantics = :exact, eps = EPS)
            for i in 1:n; fix(P[i], p[i]; force = true); end
            @objective(m, Max, 0.0 * P[1]); optimize!(m)
            st = termination_status(m)
            if st != OPTIMAL
                nbad += 1
                println("  ✗ 不可行：preds=$preds n=$n margin=$(round(mg,digits=5)) p=", round.(p, digits=4), " st=$st")
            end
        end
        println("  preds=$preds n=$n 完成"); flush(stdout)
    end
    println("校验：$ntest 例（跳过薄层 $nskip 例），$nbad 个问题")
end
main()
