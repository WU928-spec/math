# a4_feat3.jl —— 修正版：只在"反例域"里提取片特征
#   反例域 = {所有工件 > α' = 4/15, 且已归一化到 C* = 1}（L1 保证任何极小反例都在此域内）
#   对该域内的片求 LP 天花板（装箱枚举只需 ≤3 件/机，因 4 件 > 4α' > 1），
#   并提取"定义性比较"，为"按比较划分情形"提供依据。
include("a4_lib.jl")
using JuMP, HiGHS
const RHO   = C_TARGET
const RHO_T = 1.2
const ALP = 4/15; const TARGET_PIECES = parse(Int, ARGS[2]); const RNGSEED = parse(Int, ARGS[1]);

function trace(p)
    n = length(p); load = zeros(4); a = zeros(Int, n); E = [Int[] for _ in 1:n]
    for j in 1:min(4, n); a[j] = j; load[j] += p[j]; end
    lam = (p[4] + p[5] > p[1]) ? :p45 : :p1
    τ = RHO * max(p[1], p[4] + p[5])
    for j in 5:n
        Ej = [m for m in 1:4 if load[m] + p[j] <= τ + 1e-15]; E[j] = copy(Ej)
        a[j] = isempty(Ej) ? argmin(load) : Ej[argmax(load[Ej])]
        load[a[j]] += p[j]
    end
    return a, E, lam, argmax(load)
end
key(p) = (t = trace(p); string(length(p), "|", t[1], "|", t[2], "|", t[3], "|", t[4]))

"片内 LP 天花板（P ≥ ALP, 装箱 ≤3 件/机）；不可行则返回 NaN"
function ceiling(p0)
    p = p0 ./ opt_makespan(p0, 4); n = length(p); a, E, lam, am = trace(p)
    best = -Inf; bp = Float64[]; anyfeas = false
    for blocks in partitions(n, 3, 4)
        m = Model(HiGHS.Optimizer); set_silent(m)
        @variable(m, P[1:n]); for i in 1:n; set_lower_bound(P[i], ALP); end
        for i in 1:(n-1); @constraint(m, P[i] >= P[i+1]); end
        for blk in blocks; @constraint(m, sum(P[i] for i in blk) <= 1.0); end
        lam == :p1 ? @constraint(m, P[1] >= P[4]+P[5]) : @constraint(m, P[4]+P[5] >= P[1])
        load = [AffExpr(0.0) for _ in 1:4]; for j in 1:min(4, n); load[j] += P[j]; end
        τ = RHO * (lam == :p1 ? P[1] : P[4]+P[5])
        for j in 5:n
            pre = copy(load); aa = a[j]; Ej = E[j]
            for mm in 1:4
                mm in Ej ? @constraint(m, pre[mm] + P[j] <= τ) : @constraint(m, pre[mm] + P[j] >= τ)
            end
            if isempty(Ej); for mm in 1:4; @constraint(m, pre[aa] <= pre[mm]); end
            else;           for mm in Ej;   @constraint(m, pre[aa] >= pre[mm]); end; end
            load[aa] += P[j]
        end
        for mm in 1:4; @constraint(m, load[am] >= load[mm]); end
        @objective(m, Max, load[am]); optimize!(m)
        if termination_status(m) == OPTIMAL
            anyfeas = true
            if objective_value(m) > best + 1e-12; best = objective_value(m); bp = value.(P); end
        end
    end
    return anyfeas ? (best, bp, (a, E, lam, am)) : (NaN, Float64[], (a, E, lam, am))
end

function feats(p, a, E, lam)
    n = length(p)
    return Dict{String,Any}(
        "n" => n, "lam" => string(lam),
        "nE" => count(j -> !isempty(E[j]), 5:n), "nFB" => count(j -> isempty(E[j]), 5:n),
        "prof" => [count(==(mm), a) for mm in 1:4],
        "p1≥p45" => p[1] >= p[4]+p[5], "p3≥p45" => p[3] >= p[4]+p[5],
        "p2≥p3+p4" => p[2] >= p[3]+p[4], "p5≥p3" => p[5] >= p[3],
        "p4+p5≥p2" => p[4]+p[5] >= p[2], "p1≥p2+p5" => p[1] >= p[2]+p[5],
        "M1收件" => a[5] == 1 || any(j -> j >= 5 && a[j] == 1, 5:n))
end

function main()
    rng = MersenneTwister(RNGSEED); seen = Set{String}(); rows = []; nempty = 0; ntot = 0
    while length(rows) < TARGET_PIECES
        n = rand(rng, 9:12)
        p = rand(rng) < 0.6 ? sort(Float64[rand(rng, 1:10)/10 for _ in 1:n]; rev = true) :
                              sort(Float64[ALP + rand(rng)*(1-ALP) for _ in 1:n]; rev = true)
        cs = opt_makespan(p, 4); pn = p ./ cs
        minimum(pn) < ALP - 1e-12 && continue           # 不在反例域，跳过（其片必空）
        k = key(pn); k in seen && continue
        r = a4_sim(pn, A4(C_TARGET, [:p1, :p45], false, false))[1] / opt_makespan(pn, 4)
        # 不按比值过滤：要覆盖低天花板的多样子
        push!(seen, k); ntot += 1
        c, cp, (a, E, lam, am) = ceiling(pn)
        isnan(c) && continue
        f = feats(cp, a, E, lam)
        println(join([RNGSEED, length(rows)+1, f["n"], round(c, digits = 6), f["lam"], f["nE"], f["nFB"],
                      join(f["prof"], "-"), f["p2≥p3+p4"] ? 1 : 0, f["p3≥p45"] ? 1 : 0,
                      f["p5≥p3"] ? 1 : 0, f["p4+p5≥p2"] ? 1 : 0, f["M1收件"] ? 1 : 0,
                      round(minimum(cp), digits = 4)], "\t")); flush(stdout)
        push!(rows, (1.0, c, cp, f))
    end
    println("\n进入反例域的采样片数 ", ntot, "；其中在 α' 域内为空（被剪枝）", nempty)
    hi = filter(x -> x[2] > 1.19, rows)
    println("天花板 > 1.19 的片：", length(hi), " / ", length(rows))
    for (r, c, cp, f) in hi
        println("   c=", round(c, digits = 6), " 实例=", round.(cp, digits = 4))
        println("      特征=", f)
    end
end
main()
