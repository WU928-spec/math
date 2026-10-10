# §5.11j 关键轨迹引理核验：位次 3（M4 收 p7）时，步 8 接收机 M_c 在步 7 必不合格（p_c + p7 > τ）
include("/Users/a123456/math/半在线研究/SOSDP上界_algA_5over4/code/m3_a3_verify/jl/a4_lib.jl")
using Random, Printf

function main(N)
    rng = MersenneTwister(4242)
    tot = 0; bad = 0; lowseg = 0; bad_low = 0
    min_slack = Inf   # p_c + p7 − τ（应恒 > 0）
    for _ in 1:N
        n = 9
        p = gen_instance(n, rng; family = rand(rng, (:blocks, :pow, :two, :general)))
        cs = opt_makespan(p, 4); pn = p ./ cs
        pn[end] < 4 / 15 - 1e-12 && continue
        load = copy(pn[1:4]); cnt = ones(Int, 4)
        Λ = max(pn[1], pn[4] + pn[5]); τ = C_TARGET * Λ
        recv = zeros(Int, 4); ok = false; mR = 0
        load7 = 0.0; c7 = 0
        for j in 5:n
            E = [m for m in 1:4 if load[m] + pn[j] <= τ + 1e-15]
            if j == 7
                # 步 7 放置前：找出尚未收件的机器（应只剩 M4 与 M_c）
                unfin = [m for m in 1:4 if cnt[m] == 1]
                if length(unfin) == 2 && 4 in unfin
                    c7 = unfin[unfin .!= 4][1]
                    load7 = load[c7]
                end
            end
            m = isempty(E) ? argmin(load) : E[argmax(load[E])]
            if j <= n - 1; recv[j - 4] = m; else ok = isempty(E); mR = m; end
            load[m] += pn[j]; cnt[m] += 1
        end
        ok || continue
        cnt[mR] -= 1
        sort(cnt; rev = true) == [2, 2, 2, 2] || continue
        recv[3] == 4 || continue                # 位次 3
        c7 >= 1 || continue
        recv[4] == c7 || continue               # M_c 确实是步 8 接收机
        tot += 1
        slack = load7 + pn[7] - τ               # p_c + p7 − τ，应 > 0（不合格）
        slack < min_slack && (min_slack = slack)
        if slack <= 1e-12
            bad += 1
            @printf("反例: p_c+p7-τ=%.6f p=%s\n", slack, string(round.(pn; digits = 4)))
        end
        if pn[end] <= 0.3 + 1e-12
            lowseg += 1
            slack <= 1e-12 && (bad_low += 1)
        end
    end
    @printf("位次3 实例 %d 条（其中 z≤3/10 段 %d 条）；步7 M_c 合格（违例）%d 条（段内 %d）；p_c+p7−τ 最小值 %.6f\n",
        tot, lowseg, bad, bad_low, min_slack)
end
main(120000)
