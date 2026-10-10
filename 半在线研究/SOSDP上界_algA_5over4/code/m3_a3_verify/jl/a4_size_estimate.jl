# a4_size_estimate.jl —— 只做"规模侦察"：各 (n, Λ 分支) 下采样，数一数不同的片有多少
#   纯 Julia（用 opt_makespan 归一化），不跑 MILP ⟹ 极轻
#   用法：julia --project=. a4_size_estimate.jl <每配置样本数>
include("a4_lib.jl")
using Random

const ALP = 4.0 / 15.0
const RHO = C_TARGET

"返回 (片key, 各算法机最多件数)"
function trace_key(p)
    n = length(p); load = zeros(4); cnt = zeros(Int, 4)
    a = zeros(Int, n); E = [Int[] for _ in 1:n]
    for j in 1:min(4, n); a[j] = j; load[j] += p[j]; cnt[j] += 1; end
    lam = (n >= 5 && p[4] + p[5] > p[1]) ? "p45" : "p1"
    τ = RHO * max(p[1], n >= 5 ? p[4] + p[5] : 0.0)
    for j in 5:n
        Ej = [m for m in 1:4 if load[m] + p[j] <= τ + 1e-15]; E[j] = collect(Ej)
        a[j] = isempty(Ej) ? argmin(load) : Ej[argmax(load[Ej])]
        load[a[j]] += p[j]; cnt[a[j]] += 1
    end
    return string(n, "|", lam, "|", join(a[5:n], "-"), "|",
                  join([join(sort(E[j]), "") for j in 5:n], "-")), maximum(cnt)
end

function run(N::Int)
    rng = MersenneTwister(2026)
    for n in 5:12
        seen = Dict{String,Int}(); nf = 0; maxcnt = 0; bestr = 0.0; bestp = Float64[]
        a4 = A4(C_TARGET, [:p1, :p45], false, false)
        tries = 0
        while nf < N && tries < 40 * N
            tries += 1
            p = sort(Float64[rand(rng, 1:20) / 20 for _ in 1:n]; rev = true)
            cs = opt_makespan(p, 4)
            pn = p ./ cs
            minimum(pn) < ALP - 1e-12 && continue
            if n >= 5
                (pn[4] + pn[5] > pn[1]) || (pn[1] > pn[4] + pn[5]) || continue   # 避免正好并列
            end
            nf += 1
            k, mc = trace_key(pn); maxcnt = max(maxcnt, mc)
            seen[k] = get(seen, k, 0) + 1
            r = a4_sim(pn, a4)[1]
            r > bestr && (bestr = r; bestp = pn)
        end
        np1 = count(k -> occursin("|p1|", k), keys(seen))
        np45 = length(seen) - np1
        println("n=", rpad(n, 3), " 家族样本 ", rpad(nf, 6),
                " 不同片 ", rpad(length(seen), 6), "（Λ=p1: ", rpad(np1, 5), " Λ=p45: ", rpad(np45, 5), "）",
                " 每机最多件数 ", maxcnt, "  最大比值 ", round(bestr, digits = 5))
        flush(stdout)
    end
end

run(parse(Int, ARGS[1]))
