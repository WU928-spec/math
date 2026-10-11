# 真模拟器重放 ε=0.01 内缩见证
include("a4_lib.jl")
using Printf
function main()
    pn = [0.6328, 0.5411, 0.5411, 0.4589, 0.4493, 0.4493, 0.3672, 0.2754, 0.2754]
    cs = opt_makespan(pn, 4); pn = pn ./ cs
    println("C* = ", cs, "  p = ", round.(pn; digits=6))
    n = 9; load = copy(pn[1:4])
    Λ = max(pn[1], pn[4] + pn[5]); τ = C_TARGET * Λ
    lpt = false
    println("τ=$(round(τ,digits=6))  Λ=$(round(Λ,digits=6))  p1+p5=$(round(pn[1]+pn[5],digits=6))  p1+p5-τ=$(round(pn[1]+pn[5]-τ,digits=6))")
    for j in 5:n
        E = [m for m in 1:4 if load[m] + pn[j] <= τ + 1e-12]
        mm = isempty(E) ? argmin(load) : (lpt ? E[argmin(load[E])] : E[argmax(load[E])])
        margins = [(m, round(load[m]+pn[j]-τ, digits=5)) for m in 1:4]
        @printf("步%d p=%.6f E=%s 模式=%s 落点=M%d  各机（负载+p-τ）=%s\n", j, pn[j], E,
                isempty(E) ? "兜底" : (lpt ? "lightest" : "fullest"), mm, string(margins))
        j == 5 && mm != 1 && (lpt = true)
        load[mm] += pn[j]
    end
    pre = copy(load); r = argmin(load); pre[r] -= pn[n]
    @printf("终载=%s\n放z前 min=%.8f  min+z=%.8f  vs ρ=%.8f  超出=%.8f\n",
            string(round.(load;digits=4)), minimum(pre), minimum(pre)+pn[n], C_TARGET, minimum(pre)+pn[n]-C_TARGET)
end
main()
