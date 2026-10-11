# 干净反例见证：全精度 LP 见证 → 独立重放 → 扰动稳健性
include("a4_lib.jl")
include("h5i_shape_seal_lib.jl")
using Printf

function replay(pn)
    n = length(pn); load = copy(pn[1:4])
    Λ = max(pn[1], pn[4] + pn[5]); τ = C_TARGET * Λ
    lpt = false; tr = Int[]
    for j in 5:n
        E = [m for m in 1:4 if load[m] + pn[j] <= τ + 1e-12]
        mm = isempty(E) ? argmin(load) : (lpt ? E[argmin(load[E])] : E[argmax(load[E])])
        push!(tr, mm)
        j == 5 && mm != 1 && (lpt = true)
        load[mm] += pn[j]
    end
    return maximum(load), tr
end

function main()
    k = [2, 4, 3, 1, 1]; masks = [14, 12, 5, 1, 0]
    v, p = h5i_eps_witness(9, k, masks, :L, 0.01)   # 全精度见证
    cs = opt_makespan(p, 4); pn = p ./ cs
    mk, tr = replay(pn)
    @printf("见证(全精度): p=%s\n", string(round.(pn; digits = 8)))
    @printf("C*=%.10f 轨迹=%s 比值=%.8f  超出ρ %+.8f\n", cs, tr, mk, mk - C_TARGET)
    # 扰动稳健性：每件 ±0.002 随机扰动 200 次，比值 >ρ 的比例
    rng = MersenneTwister(1); nbad = 0; worst = Inf
    for _ in 1:200
        q = pn .* (1 .+ 0.004 .* (rand(rng, 9) .- 0.5))
        sort!(q; rev = true)
        csq = opt_makespan(q, 4); q ./= csq
        mq, _ = replay(q)
        mq > C_TARGET && (nbad += 1)
        worst = min(worst, mq)
    end
    @printf("扰动 200 次：比值>ρ 的 %d 次，最小比值 %.8f\n", nbad, worst)
end
main()
