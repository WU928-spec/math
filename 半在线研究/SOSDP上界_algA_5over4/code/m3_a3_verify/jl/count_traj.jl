include("a4_lib.jl")
const RHO = C_TARGET
function trajkey(p)
    n = length(p); load = zeros(4); a = zeros(Int,n); E = [Int[] for _ in 1:n]
    for j in 1:min(4,n); a[j]=j; load[j]+=p[j]; end
    lam = (p[4]+p[5] > p[1]) ? :p45 : :p1
    τ = RHO*max(p[1],p[4]+p[5])
    for j in 5:n
        Ej = [m for m in 1:4 if load[m]+p[j] <= τ+1e-15]; E[j]=copy(Ej)
        a[j] = isempty(Ej) ? argmin(load) : Ej[argmax(load[Ej])]
        load[a[j]] += p[j]
    end
    return string(n,"|",a,"|",E,"|",lam,"|",argmax(load))
end
# (i) 随机采样下的可达轨迹数（下界）
function cnt()
    rng = MersenneTwister(1); keys_all = Set{String}(); keys_hi = Set{String}(); N = 0
    for n in 5:12, _ in 1:6000
        p = rand(rng, n); sort!(p; rev=true); N += 1
        k = trajkey(p); push!(keys_all, k)
        a4_sim(p, A4(C_TARGET,[:p1,:p45],false,false))[1]/opt_makespan(p,4) >= 1.10 && push!(keys_hi, k)
    end
    println("随机采样 ", N, " 个实例：不同轨迹总数 = ", length(keys_all),
            "；其中比值 ≥1.10 的 = ", length(keys_hi))
    # (ii) n=12 全 0.5 附近的轨迹（最坏家族）以及"格点"枚举下的轨迹数
    ks = Set{String}()
    for n in 8:12
        for t in 1:20000
            p = Float64[rand(rng,1:10)/10 for _ in 1:n]; sort!(p; rev=true); push!(ks, trajkey(p))
        end
    end
    println("格点(k/10)采样 100k 个实例（n=8..12）：不同轨迹 = ", length(ks))
    # (iii) 分配模式的理论上界
    println("理论上界：Σ_{n=5..12} 4^(n-4) = ", sum(4^(n-4) for n in 5:12),
            "（n=12 单档 4^8 = ", 4^8, "）")

end
cnt()
