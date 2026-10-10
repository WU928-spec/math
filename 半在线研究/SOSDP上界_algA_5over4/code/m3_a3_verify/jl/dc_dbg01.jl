include("dc_dff.jl")
using Random
const ALP = 4.0 / 15.0
rng = MersenneTwister(5)
found = 0
for t in 1:40000
    n = 10
    p = gen_instance(n, rng; lower = ALP + 1e-9, family = rand(rng, (:pow, :blocks, :two)))
    cs = opt_makespan(p, 4); pn = p ./ cs
    minimum(pn) < ALP - 1e-9 && continue
    pn[4] + pn[5] >= pn[1] - 1e-12 || continue
    τ = C_TARGET * max(pn[1], pn[4] + pn[5])
    ld = zeros(4); nf = zeros(Int, 4); nb = zeros(Int, 4); jp = zeros(Int, 4)
    for j in 1:4; ld[j] += pn[j]; end
    for j in 5:n
        E = [mm for mm in 1:4 if ld[mm] + pn[j] <= τ + 1e-15]
        aj = isempty(E) ? argmin(ld) : E[argmax(ld[E])]
        isempty(E) ? (nb[aj] += 1; jp[aj] == 0 && (jp[aj] = j)) : (nf[aj] += 1)
        ld[aj] += pn[j]
    end
    Rz = argmax(ld)
    # (0,1) 接收机：0 填充 + 恰 1 次兜底（最后一次兜底是 z 本身，故 nb[Rz]==2 表示此前 1 次 + z）
    if nf[Rz] == 0 && nb[Rz] == 2 && jp[Rz] > 0
        println("找到 (0,1) 实例 t=$t: 接收机 M$Rz  首次兜底 jp=$(jp[Rz])")
        println("   p = ", round.(pn, digits=4))
        v = case_01(n, Int(jp[Rz]), Rz, :full45, 2, 60.0)
        println("   case_01(full45, L2) = ", v)
        found += 1
        found >= 3 && break
    end
end
found == 0 && println("未找到 (0,1) 实例")
