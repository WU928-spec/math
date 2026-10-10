# a3_prime.jl —— 对照实验：把"紧 cap + best-fit/fallback"配方直接用到 m=3
# A3' : 开局 p1..p3 各一台；Λ = max{p1, p3+p4}；τ = ρ·Λ；
#       j>=4：E={M: ℓ+pj <= τ} 取最大者，否则取最小者。
# 若 A3' 在 m=3 上也能达到 c，说明 A3 的额外机制（M1 槽、双分支、L 精化）不是"必需"的；
# 若 A3' 明显 > c，则说明这配方在 m=3 不够，m=4 的"够"就更值得怀疑。
include("a4_lib.jl")

function a3p_sim(p::Vector{Float64}, rho::Float64)
    n = length(p); load = zeros(3); asg = [Int[] for _ in 1:3]
    put(j, m) = (load[m] += p[j]; push!(asg[m], j))
    for j in 1:min(3, n); put(j, j); end
    n <= 3 && return maximum(load)
    Λ = max(p[1], p[3] + p[4]); τ = rho * Λ
    for j in 4:n
        E = [m for m in 1:3 if load[m] + p[j] <= τ]
        put(j, isempty(E) ? argmin(load) : E[argmax(load[E])])
    end
    return maximum(load)
end

function search_a3p(rho; nrange = 5:9, per = 3000, seed = 21)
    rng = MersenneTwister(seed); worst = 0.0; wit = Float64[]; wn = 0
    for n in nrange, fam in (:pow, :blocks, :two, :tight, :general)
        for _ in 1:per
            p = gen_instance(n, rng; family = fam, lower = fam == :general ? 0.0 : ALPHA + 1e-9)
            r = a3p_sim(p, rho) / opt_makespan(p, 3)
            r > worst && (worst = r; wit = copy(p); wn = n)
        end
    end
    return worst, wit, wn
end

println("m=3：A3'（紧 cap 版）与真正的 A3、与 LPT 的对照")
println("-"^80)
for rho in (5/4, 1.2, C_TARGET, 1.15)
    w, p, n = search_a3p(rho)
    println("A3'(ρ=", rpad(round(rho, digits = 5), 8), ") 最坏比值 = ", rpad(round(w, digits = 6), 10),
            " n=", lpad(n, 2), "   ", (w <= C_TARGET + 1e-9 ? "<= c" : "> c ✗"))
    w > C_TARGET + 1e-9 && println("      见证 p = ", round.(p, digits = 4))
end
function control()
    # 对照：真正的 A3（common.jl 里的 a3_sim）与 LPT
    rng = MersenneTwister(21); wA3 = 0.0; wLPT = 0.0
    for n in 5:9, _ in 1:3000
        p = gen_instance(n, rng; family = :pow)
        wA3 = max(wA3, a3_sim(p)[1] / opt_makespan(p, 3))
        load = zeros(3); for x in p; load[argmin(load)] += x; end; wLPT = max(wLPT, maximum(load)/opt_makespan(p, 3))
    end
    println("\n对照（同族随机样本）：A3 最坏比值 = ", round(wA3, digits = 6), "；LPT = ", round(wLPT, digits = 6))

end
control()
