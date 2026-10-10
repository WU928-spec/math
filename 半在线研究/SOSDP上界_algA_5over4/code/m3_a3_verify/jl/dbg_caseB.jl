include("a4_lib.jl")
using Random
function run()
    rng = MersenneTwister(31); a4 = A4(C_TARGET, [:p1,:p45], false, false)
    best=0.0; bestp=Float64[]; ncase=0
    for it in 1:600000
        n = rand(rng, 9:12)
        p = sort(Float64[rand(rng,1:20)/20 for _ in 1:n]; rev=true)
        cs = opt_makespan(p,4); pn = p./cs
        minimum(pn) < 4/15 - 1e-12 && continue
        load = zeros(4); τ = C_TARGET*max(pn[1],pn[4]+pn[5])
        for j in 1:min(4,n); load[j]+=pn[j]; end
        fb = Bool[]
        for j in 5:n
            E=[m for m in 1:4 if load[m]+pn[j] <= τ+1e-15]
            push!(fb, isempty(E))
            load[ isempty(E) ? argmin(load) : E[argmax(load[E])] ] += pn[j]
        end
        (fb[end] && !fb[end-1]) || continue        # z 兜底 & n-1 步填充（= 情形 B）
        ncase += 1
        r = a4_sim(pn, a4)[1]/opt_makespan(pn, 4)
        r > best && (best=r; bestp=copy(pn))
    end
    println("情形 B（z 兜底 & n-1 步填充）实例 ", ncase, " 个；最大比值 = ", round(best,digits=6))
    println("   见证 = ", round.(bestp,digits=4))
end
run()
