include("/Users/a123456/math/半在线研究/SOSDP上界_algA_5over4/code/m3_a3_verify/jl/a4_lib.jl")
using Printf
function main()
    p = [0.8592, 0.7677, 0.7628, 0.7439, 0.719, 0.6712, 0.569, 0.288]
    cs = opt_makespan(p, 4)
    ρ = C_TARGET
    n = length(p); load = copy(p[1:4])
    Λ = max(p[1], p[4] + p[5]); τ = ρ * Λ
    lpt = false; rec = Int[]
    for j in 5:n
        E = [m for m in 1:4 if load[m] + p[j] <= τ + 1e-15]
        m = isempty(E) ? argmin(load) : (lpt ? E[argmin(load[E])] : E[argmax(load[E])])
        j == 5 && m != 1 && (lpt = true)
        push!(rec, m); load[m] += p[j]
    end
    @printf("C* = %.6f，H5i makespan = %.6f，比值 = %.8f（ρ = %.8f，差 %+.2e）\n",
            cs, maximum(load), maximum(load) / cs, ρ, maximum(load) / cs - ρ)
    @printf("Λ = %.6f，τ = %.6f，轨迹 = %s，lpt 切换 = %s\n", Λ, τ, string(rec), string(lpt))
    println("终载 = ", round.(load, digits=4), "；体积 = ", round(sum(p), digits=4), "，体积/4 = ", round(sum(p) / 4, digits=4))
end
main()
