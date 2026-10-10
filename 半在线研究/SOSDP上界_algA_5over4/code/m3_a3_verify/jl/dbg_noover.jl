include("a4_lib.jl")
using Random
# 找"放 z 前全部机 ≤ τ（无超载）且最终 > 6/5"的实例
function run()
rng = MersenneTwister(7); a4 = A4(C_TARGET, [:p1,:p45], false, false)
nfound=0; nfb=0; best=0.0; bestp=Float64[]
for it in 1:600000
    n = rand(rng, 9:12)
    p = sort(Float64[rand(rng,1:20)/20 for _ in 1:n]; rev=true)
    cs = opt_makespan(p,4); pn = p./cs
    minimum(pn) < 4/15 - 1e-12 && continue
    # 重放，记录"放 z 之前"的负载与 τ
    load = zeros(4); τ = C_TARGET*max(pn[1],pn[4]+pn[5])
    for j in 1:min(4,n); load[j]+=pn[j]; end
    fb=false; mR=0
    for j in 5:n
        E=[m for m in 1:4 if load[m]+pn[j] <= τ+1e-15]
        aj = isempty(E) ? argmin(load) : E[argmax(load[E])]
        if j==n; fb = isempty(E); mR = aj; end
        load[aj]+=pn[j]
    end
    fb || continue; nfb+=1
    # 放 z 前：除 mR 外各机负载 + (mR 减去 z)
    pre = copy(load); pre[mR]-=pn[n]
    if maximum(pre) <= τ + 1e-9          # 无超载
        final = pre[mR]+pn[n]
        if final > 1.2+1e-9
            nfound+=1
            final/cs > best && (best=final/cs; bestp=copy(pn))
        end
    end
end
println("兜底实例 ", nfb, "；其中『无超载且最终>6/5』: ", nfound)
nfound>0 && println("   实例 = ", round.(bestp,digits=4))
end
run()
