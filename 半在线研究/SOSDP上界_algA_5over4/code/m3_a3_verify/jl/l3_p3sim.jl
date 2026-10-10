include("/Users/a123456/math/半在线研究/SOSDP上界_algA_5over4/code/m3_a3_verify/jl/a4_lib.jl")
using Printf
function trace_show(p)
    cs = opt_makespan(p, 4); pn = p ./ cs
    Λ = max(pn[1], pn[4] + pn[5]); τ = C_TARGET * Λ
    println("C*=", round(cs, digits=5), "  Λ=", round(Λ, digits=5), "  τ=", round(τ, digits=5))
    load = copy(pn[1:4]); cnt = ones(Int, 4)
    for j in 5:length(pn)
        E = [m for m in 1:4 if load[m] + pn[j] <= τ + 1e-12]
        m = isempty(E) ? argmin(load) : E[argmax(load[E])]
        @printf("步%d p=%.4f E=%s -> M%d  (loads %s)\n", j, pn[j], isempty(E) ? "∅" : string(E), m, join(round.(load, digits=3), ","))
        load[m] += pn[j]; cnt[m] += 1
    end
    println("终载: ", round.(load, digits=4))
end
# 主线位次3紧实例 + 其理论族形 (a²,c²,d³,z²) 边界点
trace_show([0.6524, 0.6212, 0.4986, 0.4986, 0.3413, 0.3406, 0.3406, 0.3312, 0.3282])
println("--- 理论边界族 a+d=1, c=1/2, c+d=1/ρ, d+2z=1 ---")
ρ = C_TARGET; d = 1 / ρ - 1 / 2; a = 1 - d; z = (1 - d) / 2
trace_show([a, a, 0.5, 0.5, d, d, d, z, z])
