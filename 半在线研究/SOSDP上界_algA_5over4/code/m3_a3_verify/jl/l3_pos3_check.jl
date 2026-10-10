# 位次 3（M4 收 p7）天花板核验：
#  (1) 族 (a^2,c^2,d^3,z^2) 的精确逐步重放 —— 检验它落位次几、min+z 是多少
#  (2) 随机搜索位次-3 实例（层 3 形状 {2,2,2,2}、z 兜底、M4 在步 7 收件）的 max(min+z)
include("/Users/a123456/math/半在线研究/SOSDP上界_algA_5over4/code/m3_a3_verify/jl/a4_lib.jl")
using Random, Printf

const RHO = C_TARGET

function trace(p; label="")
    pn = p ./ opt_makespan(p, 4)
    Λ = max(pn[1], pn[4] + pn[5]); τ = RHO * Λ
    load = copy(pn[1:4]); recv = zeros(Int, 4)
    println("── $label")
    @printf("p = %s\n   Λ=%.6f  τ=%.6f  (C*=1 归一化后)\n", string(round.(pn, digits=6)), Λ, τ)
    for j in 5:9
        E = [m for m in 1:4 if load[m] + pn[j] <= τ + 1e-15]
        m = isempty(E) ? argmin(load) : E[argmax(load[E])]
        @printf("步%d  p%d=%.6f  E=%s  → M%d（%s） 负载=%s\n",
                j, j, pn[j], string(E), m, isempty(E) ? "兜底" : "填充", string(round.(load, digits=4)))
        load[m] += pn[j]; recv[m] = j
    end
    z = pn[9]; pre = copy(load); pre[argmax([recv[m]==9 for m in 1:4])] -= z
    @printf("M4 收件位次: p%d ; min(pre)=%.6f ; min+z = %.6f\n\n", recv[4], minimum(pre), minimum(pre)+z)
    return recv[4], minimum(pre)+z
end

function main()
    # ---------- (1) 族精确重放
    d = 1/RHO - 1/2; a = 1 - d; zv = (1 - d)/2
    @printf("ρ=%.7f  d=%.7f  a=%.7f  z=%.7f  (c=0.5)\n", RHO, d, a, zv)
    trace([a, a, 0.5, 0.5, d, d, d, zv, zv]; label="族 (a²,c²,d³,z²) 精确")
    @printf("对照值：3/4+1/(2ρ) = %.6f ; c+d+z = %.6f ; c+2z = %.6f\n\n", 0.75+1/(2RHO), 0.5+d+zv, 0.5+2zv)

    # ---------- (2) 位次 3 随机搜索
    rng = MersenneTwister(7); N = 150_000
    tot = 0; best = -Inf; bp = Float64[]
    fambase = [a, a, 0.5, 0.5, d, d, d, zv, zv]
    razor   = [7/12, 7/12, 0.5, 0.5, 5/12, 5/12, 1/3, 1/3, 1/3]
    for _ in 1:N
        fam = rand(rng, (:grid, :fam, :razor))
        p = if fam == :grid
            k = rand(rng, 1:3); vals = sort(rand(rng, 3:10, k) ./ 10; rev = true)
            q = Float64[]; while length(q) < 9; push!(q, vals[rand(rng, 1:k)]); end
            sort(q; rev = true)
        else
            base = fam == :fam ? fambase : razor
            sort([b0 * (1 + 0.10 * (rand(rng) - 0.5)) for b0 in base]; rev = true)
        end
        pn = p ./ opt_makespan(p, 4)
        pn[9] < 4/15 - 1e-12 && continue
        Λ = max(pn[1], pn[4] + pn[5]); τ = RHO * Λ
        load = copy(pn[1:4]); cnt = ones(Int, 4)
        okz = false; mR = 0; recv4 = 0; bad = false
        for j in 5:9
            E = [m for m in 1:4 if load[m] + pn[j] <= τ + 1e-15]
            m = isempty(E) ? argmin(load) : E[argmax(load[E])]
            if j == 9; okz = isempty(E); mR = m; end
            if j <= 8 && m == 4; recv4 = j; end
            load[m] += pn[j]; cnt[m] += 1
        end
        okz || continue                      # z 兜底
        recv4 == 7 || continue               # M4 在步 7 收 p7（位次 3）
        cnt[mR] -= 1
        sort(cnt; rev = true) == [2, 2, 2, 2] || continue   # 层 (3) 形状
        tot += 1
        z = pn[9]; pre = copy(load); pre[mR] -= z
        v = minimum(pre) + z
        if v > best; best = v; bp = pn; end
    end
    @printf("位次-3 层(3)实例 %d 条；max(min+z) = %.6f\n", tot, best)
    @printf("最差实例 p = %s\n", string(round.(bp, digits=6)))
    @printf("对照：3/4+1/(2ρ) = %.6f，ρ = %.6f，6/5 = 1.2\n", 0.75+1/(2RHO), RHO)
end
main()
