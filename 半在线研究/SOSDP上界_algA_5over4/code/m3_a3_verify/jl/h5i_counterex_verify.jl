include("/Users/a123456/math/半在线研究/SOSDP上界_algA_5over4/code/m3_a3_verify/jl/a4_lib.jl")
using Printf
function main()
    p = [0.63284270, 0.54105338, 0.54105338, 0.45894662, 0.44926405, 0.44926405, 0.36715730, 0.27536797, 0.27536797]
    cs = opt_makespan(p, 4)
    n = length(p); load = copy(p[1:4])
    Λ = max(p[1], p[4] + p[5]); τ = C_TARGET * Λ
    lpt = false; rec = Int[]
    @printf("τ = %.6f，Λ = %.6f，p1+p5−τ = %+.6f\n", τ, Λ, p[1] + p[5] - τ)
    for j in 5:n
        E = [m for m in 1:4 if load[m] + p[j] <= τ + 1e-15]
        m = isempty(E) ? argmin(load) : (lpt ? E[argmin(load[E])] : E[argmax(load[E])])
        j == 5 && m != 1 && (lpt = true)
        push!(rec, m); load[m] += p[j]
    end
    println("轨迹 = ", rec, "  lpt = ", lpt)
    println("终载 = ", round.(load, digits = 6))
    @printf("C* = %.6f，H5i makespan = %.6f\n", cs, maximum(load))
    @printf("比值 = %.8f，ρ = %.8f，超出 %+.2e\n", maximum(load) / cs, C_TARGET, maximum(load) / cs - C_TARGET)
end
main()
