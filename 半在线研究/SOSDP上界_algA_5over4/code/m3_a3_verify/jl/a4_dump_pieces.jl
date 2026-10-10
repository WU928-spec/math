# a4_dump_pieces.jl —— 采样家族实例，把命中的不同"片"按叶子格式落盘（供 a4_leaf10_level.jl 检验）
#   用法：julia --project=. a4_dump_pieces.jl <样本数> <seed> <输出文件>
include("a4_lib.jl")
using Random

const ALP = 4.0 / 15.0
const NT  = 10
const RHO = C_TARGET

function trace10(p)
    load = zeros(4); a = zeros(Int, NT); E = [Int[] for _ in 1:NT]
    for j in 1:4; a[j] = j; load[j] += p[j]; end
    τ = RHO * (p[4] + p[5])
    for j in 5:NT
        Ej = [m for m in 1:4 if load[m] + p[j] <= τ + 1e-15]; E[j] = collect(Ej)
        a[j] = isempty(Ej) ? argmin(load) : Ej[argmax(load[Ej])]
        load[a[j]] += p[j]
    end
    return a, E
end

function main()
    N = parse(Int, ARGS[1]); seed = parse(Int, ARGS[2]); out = ARGS[3]
    rng = MersenneTwister(seed); seen = Set{String}(); rows = String[]
    for _ in 1:N
        p = sort(Float64[rand(rng, 1:20) / 20 for _ in 1:10]; rev = true)
        cs = opt_makespan(p, 4); pn = p ./ cs
        minimum(pn) < ALP - 1e-12 && continue
        (pn[4] + pn[5] >= pn[1] - 1e-12 && pn[2] <= pn[3] + pn[4] + 1e-12 &&
         pn[3] <= pn[4] + pn[5] + 1e-12 && pn[5] <= pn[3] + 1e-12) || continue
        a, E = trace10(pn)
        k = string(join(a[5:10], "-"), "|", join([join(sort(E[j]), "") for j in 5:10], "-"))
        k in seen && continue
        push!(seen, k)
        ks = a[5:10]; ms = [sum(1 << (m - 1) for m in E[j]; init = 0) for j in 5:10]
        push!(rows, join(vcat(ks, ms), "\t"))
    end
    open(out, "w") do io
        for r in rows; println(io, r); end
    end
    println("写入 ", length(rows), " 条片 → ", out)
end
main()
