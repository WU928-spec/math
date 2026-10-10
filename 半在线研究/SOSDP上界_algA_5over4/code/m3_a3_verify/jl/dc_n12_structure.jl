# dc_n12_structure.jl —— n=12 (b45) 结构分析：z=p12 落哪台机、该机内容、E12 是否恒空
include("a4_lib.jl")
using Random
const ALP = 4.0 / 15.0
const A4C = A4(C_TARGET, [:p1, :p45], false, false)

function main()
    rng = MersenneTwister(2026)
    nE12nonempty = 0; ntot = 0
    rec_content = Dict{String,Int}()     # z 接收机内容模式
    rec_laststep = Dict{String,Int}()
    sizes_hist = Dict{Vector{Int},Int}()
    for t in 1:30000
        n = 12
        p = gen_instance(n, rng; lower = ALP + 1e-9,
                         family = rand(rng, (:pow, :blocks, :two, :tight, :general)))
        cs = opt_makespan(p, 4); pn = p ./ cs
        minimum(pn) < ALP - 1e-9 && continue
        pn[4] + pn[5] >= pn[1] - 1e-12 || continue   # b45
        ntot += 1
        ms, asg, load = a4_sim(pn, A4C)
        # 重放记录 E_12
        τ = C_TARGET * max(pn[1], pn[4] + pn[5])
        ld = zeros(4)
        for j in 1:4; ld[j] += pn[j]; end
        E12 = Int[]
        for j in 5:12
            E = [mm for mm in 1:4 if ld[mm] + pn[j] <= τ + 1e-15]
            j == 12 && (E12 = E)
            aj = isempty(E) ? argmin(ld) : E[argmax(ld[E])]
            ld[aj] += pn[j]
        end
        isempty(E12) || (nE12nonempty += 1)
        Rz = findfirst(mm -> 12 in asg[mm], 1:4)
        content = sort(asg[Rz])
        key = join(content, ",")
        rec_content[key] = get(rec_content, key, 0) + 1
        rec_laststep[string(isempty(E12))] = get(rec_laststep, string(isempty(E12)), 0) + 1
        sz = sort([length(a) for a in asg])
        sizes_hist[sz] = get(sizes_hist, sz, 0) + 1
    end
    println("n=12 b45 实例 $ntot；E12 非空次数 = $nE12nonempty")
    println("机器规模分布: ", sizes_hist)
    println("z 接收机内容 top20:")
    for (k, v) in sort(collect(rec_content); by = x -> -x[2])[1:min(20, end)]
        println("   {$k}: $v")
    end
end
main()
