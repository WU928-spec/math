include("a4_lib.jl")
using Random
const ALP = 4.0/15.0; const RHO = C_TARGET
function tr(p)
    load = zeros(4); a = zeros(Int,10); E = [Int[] for _ in 1:10]
    for j in 1:4; a[j] = j; load[j] += p[j]; end
    τ = RHO*(p[4]+p[5])
    for j in 5:10
        Ej = [m for m in 1:4 if load[m]+p[j] <= τ + 1e-15]; E[j] = collect(Ej)
        a[j] = isempty(Ej) ? argmin(load) : Ej[argmax(load[Ej])]
        load[a[j]] += p[j]
    end
    return join(vcat(a[5:10], [sum(1 << (m-1) for m in E[j]; init=0) for j in 5:10]), "\t")
end
enum = Set(strip(l) for l in readlines("fam10_leaves2_all.txt") if !isempty(strip(l)))
function run()
rng = MersenneTwister(11); nseen = 0; miss = Set{String}(); nf = 0
for it in 1:400000
    p = sort(Float64[rand(rng,1:20)/20 for _ in 1:10]; rev=true)
    pn = p ./ opt_makespan(p,4)
    minimum(pn) < ALP - 1e-12 && continue
    pn[4]+pn[5] >= pn[1] - 1e-12 || continue      # 只要求 Λ=p45，不加卡点谓词
    nf += 1
    k = tr(pn); nseen += 1
    k in enum || push!(miss, k)
end
println("Λ=p45 且 C*=1 的样本 ", nf, " 条；轨迹种类去重后未出现在卡点枚举里的 = ", length(miss))
for m in first(miss, 10); println("   缺: ", m); end
end
run()
