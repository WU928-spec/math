include("a4_lib.jl")
using Random
function run()
    rng = MersenneTwister(13); ncase=0; nviol=0; ex=Float64[]
    for it in 1:400000
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
        # z=pn 兜底 且 第 n-1 步是填充（fb 对应步 5..n）
        (fb[end] && !fb[end-1]) || continue
        ncase += 1
        if abs(pn[n-1]-pn[n]) > 1e-9
            nviol += 1; isempty(ex) && (ex = copy(pn))
        end
    end
    println("『z 兜底 & 第 n-1 步填充』实例 ", ncase, " 个；其中 p_{n-1}≠p_n 的: ", nviol)
    nviol>0 && println("   反例 = ", round.(ex,digits=4))
end
run()
