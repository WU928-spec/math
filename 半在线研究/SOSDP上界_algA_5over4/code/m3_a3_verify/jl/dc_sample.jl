# dc_sample.jl —— 精确模拟采样：为每个 (branch, n) 收集同机对见证 + 比值统计
#   输出：dc_witnesses.txt（每行：branch n i j p...），dc_summary.txt
include("a4_lib.jl")
using Random, Printf

const ALP = 4.0 / 15.0
const A4C = A4(C_TARGET, [:p1, :p45], false, false)

function branch_of(p)
    b45 = p[4] + p[5] >= p[1] - 1e-12
    b1 = p[1] >= p[4] + p[5] - 1e-12
    return b45, b1
end

function gen(n::Int, rng)
    fam = rand(rng, (:pow, :pow, :blocks, :two, :tight, :general))
    p = gen_instance(n, rng; lower = ALP + 1e-9, family = fam)
    cs = opt_makespan(p, 4)
    return p ./ cs
end

function main()
    N = parse(Int, ARGS[1])
    rng = MersenneTwister(length(ARGS) >= 2 ? parse(Int, ARGS[2]) : 42)
    witIO = open("dc_witnesses.txt", "w")
    sumIO = open("dc_summary.txt", "w")
    for n in 5:12
        # pairs[i,j] = count co-located; fillcnt/ovcnt 记录同机时第 j 步是填充还是兜底
        pairs = Dict{Symbol,Dict{Tuple{Int,Int},Int}}(:b45 => Dict(), :b1 => Dict())
        fillp = Dict{Symbol,Dict{Tuple{Int,Int},Int}}(:b45 => Dict(), :b1 => Dict())
        seen = Dict{Symbol,Set{Tuple{Int,Int}}}(:b45 => Set(), :b1 => Set())
        maxr = Dict{Symbol,Float64}(:b45 => 0.0, :b1 => 0.0)
        cnt = Dict{Symbol,Int}(:b45 => 0, :b1 => 0)
        bestp = Dict{Symbol,Vector{Float64}}(:b45 => Float64[], :b1 => Float64[])
        tries = 0
        while minimum(values(cnt)) < N && tries < 40N
            tries += 1
            p = gen(n, rng)
            minimum(p) < ALP - 1e-9 && continue
            b45, b1 = branch_of(p)
            (b45 || b1) || continue
            ms, asg, load = a4_sim(p, A4C)
            r = ms  # C* = 1
            # 逐步重放以记录 fill/overflow
            τ = C_TARGET * max(p[1], p[4] + p[5])
            ld = zeros(4); isfill = Dict{Int,Bool}()
            for j in 1:4; ld[j] += p[j]; end
            for j in 5:n
                E = [mm for mm in 1:4 if ld[mm] + p[j] <= τ + 1e-15]
                isfill[j] = !isempty(E)
                aj = isempty(E) ? argmin(ld) : E[argmax(ld[E])]
                ld[aj] += p[j]
            end
            for br in (:b45, :b1)
                (br == :b45 ? b45 : b1) || continue
                cnt[br] += 1
                if r > maxr[br]; maxr[br] = r; bestp[br] = copy(p); end
                for i in 1:(n-1), j in (i+1):n
                    same = any(mm -> i in asg[mm] && j in asg[mm], 1:4)
                    same || continue
                    key = (i, j)
                    pairs[br][key] = get(pairs[br], key, 0) + 1
                    j >= 5 && isfill[j] && (fillp[br][key] = get(fillp[br], key, 0) + 1)
                    if !(key in seen[br])
                        push!(seen[br], key)
                        println(witIO, br, " ", n, " ", i, " ", j, " ", join(round.(p, digits=8), " "))
                    end
                end
            end
        end
        for br in (:b45, :b1)
            tot = sum(values(pairs[br]); init = 0)
            println(sumIO, "n=$n $br 实例=$(cnt[br]) 最大比值=$(round(maxr[br], digits=6)) 同机对种类=$(length(seen[br])) 同机事件=$tot")
            println(sumIO, "   最差实例: ", join(round.(bestp[br], digits=4), " "))
            # 列出 n=j 的对（决定性家族）
            row = String[]
            for i in 1:(n-1)
                c = get(pairs[br], (i, n), 0)
                f = get(fillp[br], (i, n), 0)
                push!(row, "($i,$n):$c" * (c > 0 ? "[f$f]" : ""))
            end
            println(sumIO, "   j=n 对: ", join(row, " "))
        end
        flush(witIO); flush(sumIO)
        println("n=$n 完成 (tries=$tries)"); flush(stdout)
    end
    close(witIO); close(sumIO)
end
main()
