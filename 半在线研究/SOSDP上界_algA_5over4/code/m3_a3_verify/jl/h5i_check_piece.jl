# 单点复核：n=9 [2,2,2,2] 片 k=2,4,3,1,1 masks=14,12,5,1,0 (mode L) 的 sup=1.185846 见证
# ① 重解该片 LP 打印 p*；② 用 H5i 真模拟器独立重放 p*（轨迹、C*、真实比值）
include("a4_lib.jl")
include("h5i_shape_seal_lib.jl")  # 见下：从 h5i_shape_seal.jl 抽出 leaf_model
using Printf

function main()
    k = [2, 4, 3, 1, 1]; masks = [14, 12, 5, 1, 0]
    v, st, pstar = leaf_model_wp(9, k, masks, :L)
    @printf("LP: sup=%.8f 状态=%s\n", v, st)
    @printf("p* = %s\n", string(round.(pstar; digits = 6)))
    # 独立重放（真模拟器，不归一化假设：先归一化 C*）
    cs = opt_makespan(pstar, 4)
    pn = pstar ./ cs
    @printf("C*(p*) = %.8f  归一化后 p = %s\n", cs, string(round.(pn; digits = 6)))
    n = 9; load = copy(pn[1:4])
    Λ = max(pn[1], pn[4] + pn[5]); τ = C_TARGET * Λ
    lpt = false
    println("逐步重放（τ=$(round(τ, digits=6))）：")
    for j in 5:n
        E = [m for m in 1:4 if load[m] + pn[j] <= τ + 1e-12]
        mm = isempty(E) ? argmin(load) : (lpt ? E[argmin(load[E])] : E[argmax(load[E])])
        @printf("  步 %d: p=%.6f  E=%s  模式=%s  落点=M%d  落前负载=%s\n", j, pn[j], E,
                isempty(E) ? "兜底" : (lpt ? "lightest" : "fullest"), mm, string(round.(load; digits = 4)))
        j == 5 && mm != 1 && (lpt = true)
        load[mm] += pn[j]
    end
    @printf("终载=%s  makespan=%.8f  真实比值=%.8f  (ρ=%.8f)\n",
            string(round.(load; digits = 4)), maximum(load), maximum(load), C_TARGET)
    pre = copy(load); pre[argmin(load)] -= pn[n]
    @printf("放z前 min=%.8f  min+z=%.8f\n", minimum(pre), minimum(pre) + pn[n])
end
main()
