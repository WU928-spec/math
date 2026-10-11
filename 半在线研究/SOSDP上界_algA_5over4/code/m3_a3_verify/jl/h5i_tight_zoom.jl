# 锁定 H5i 紧实例：worst 邻域 ±3% 细扫，全精度打印 top-3 + 逐件轨迹
include("/Users/a123456/math/半在线研究/SOSDP上界_algA_5over4/code/m3_a3_verify/jl/a4_lib.jl")
using Random, Printf

function simH5i_trace(p)
    n = length(p); load = copy(p[1:min(4, n)])
    n <= 4 && return (maximum(load), false, Int[])
    Λ = max(p[1], p[4] + p[5]); τ = C_TARGET * Λ
    lpt = false; rec = Int[]
    for j in 5:n
        E = [m for m in 1:4 if load[m] + p[j] <= τ + 1e-15]
        m = isempty(E) ? argmin(load) : (lpt ? E[argmin(load[E])] : E[argmax(load[E])])
        j == 5 && m != 1 && (lpt = true)
        push!(rec, m); load[m] += p[j]
    end
    return (maximum(load), lpt, rec)
end

function main()
    base = [0.8493, 0.7694, 0.76, 0.7472, 0.7222, 0.6806, 0.5668, 0.2845]
    rng = MersenneTwister(7)
    top = [(-Inf, Float64[]) for _ in 1:3]
    for it in 1:200_000
        p = sort([b0 * (1 + 0.03 * (rand(rng) - 0.5)) for b0 in base]; rev = true)
        r = simH5i_trace(p)[1] / opt_makespan(p, 4)
        if r > top[1][1]
            pop!(top); push!(top, (r, p)); sort!(top; by = x -> -x[1])
        end
    end
    for (r, p) in top
        @printf("r=%.10f  p=%s\n", r, string(round.(p, digits=8)))
    end
    r, p = top[1]
    mk, lpt, rec = simH5i_trace(p)
    cs = opt_makespan(p, 4)
    println("—— 最差实例轨迹 ——")
    @printf("C*=%.10f  mk=%.10f  r=%.10f  lpt=%s  轨迹=%s\n", cs, mk, mk / cs, lpt, string(rec))
end
main()
