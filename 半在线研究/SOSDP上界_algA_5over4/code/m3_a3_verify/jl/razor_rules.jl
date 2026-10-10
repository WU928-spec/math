# razor 实例上不同填充规则的对比：6/5 是问题壁垒还是规则 artifact？
# 规则变体：安全线 τ = ρΛ 不变；E 非空时分别取 最满合格(A4c) / 最轻合格(LFE)；兜底 argmin 不变。
include("/Users/a123456/math/半在线研究/SOSDP上界_algA_5over4/code/m3_a3_verify/jl/a4_lib.jl")
using Printf

function sim_variant(p; rule::Symbol)
    n = length(p); load = copy(p[1:4])
    Λ = max(p[1], p[4] + p[5]); τ = C_TARGET * Λ
    rec = Int[]
    for j in 5:n
        E = [m for m in 1:4 if load[m] + p[j] <= τ + 1e-15]
        m = if isempty(E)
            argmin(load)
        elseif rule == :fullest
            E[argmax(load[E])]
        else
            E[argmin(load[E])]
        end
        push!(rec, m); load[m] += p[j]
    end
    return maximum(load), load, rec
end

razor = [0.6, 0.5, 0.5, 0.4, 0.4, 0.4, 0.3, 0.3, 0.3, 0.3]
for rule in (:fullest, :lightest)
    mk, load, rec = sim_variant(razor; rule)
    @printf("%-8s  makespan=%.6f  终载=%s  轨迹=%s\n", rule, mk, string(round.(load, digits=3)), string(rec))
end
# 对照：Algorithm A（5/4 线，最满合格）
p = razor; load = copy(p[1:4]); τ54 = 1.25 * (p[4] + p[5]); rec = Int[]
for j in 5:10
    E = [m for m in 1:4 if load[m] + p[j] <= τ54 + 1e-15]
    m = isempty(E) ? argmin(load) : E[argmax(load[E])]
    push!(rec, m); load[m] += p[j]
end
@printf("AlgA-5/4线  makespan=%.6f  终载=%s  轨迹=%s\n", maximum(load), string(round.(load, digits=3)), string(rec))
