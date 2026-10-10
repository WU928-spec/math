# a4_hunt.jl —— 多起点轨迹跳跃：判定 A4c 是否存在天花板 > 1.2 的轨迹
#   Step A: 廉价采样（含整数格点家族）→ 按 A4c 轨迹去重 → 取比值最高的若干轨迹
#   Step B: 对每条轨迹跑 LP 天花板（= 该轨迹片内竞争比的精确上确界）
#   Step C: 汇总；若某条天花板 > 1.2，输出其见证实例
include("a4_lib.jl")
using JuMP, HiGHS

const RHOA = C_TARGET

# ---------- 轨迹记录（含每步 E 集合） ----------
function a4c_trace(p::Vector{Float64})
    n = length(p); load = zeros(4); assign = zeros(Int, n); branch = fill(:open, n)
    Esets = [Int[] for _ in 1:n]
    for j in 1:min(4, n); assign[j] = j; load[j] += p[j]; end
    n <= 4 && return (assign, branch, :none, argmax(load), maximum(load), Esets)
    Λ1 = p[1]; Λ2 = p[4] + p[5]; lam = Λ2 > Λ1 ? :p45 : :p1
    τ = RHOA * max(Λ1, Λ2)
    for j in 5:n
        E = [m for m in 1:4 if load[m] + p[j] <= τ + 1e-15]
        Esets[j] = copy(E)
        if isempty(E); assign[j] = argmin(load); branch[j] = :fb
        else; assign[j] = E[argmax(load[E])]; branch[j] = :E; end
        load[assign[j]] += p[j]
    end
    return (assign, branch, lam, argmax(load), maximum(load), Esets)
end

keyof(tr) = string(length(tr[1]), "|", tr[1], "|", tr[2], "|", tr[3], "|", tr[4])

# ---------- 轨迹片内 LP 天花板 ----------
function ceiling(p0::Vector{Float64})
    cstar = opt_makespan(p0, 4); p = p0 ./ cstar
    assign, branch, lam, am, ms, Esets = a4c_trace(p)
    n = length(p); best = -Inf; bp = Float64[]
    for blocks in partitions(n, 3, 4)
        m = Model(HiGHS.Optimizer); set_silent(m)
        @variable(m, P[1:n] >= 0)
        for i in 1:(n-1); @constraint(m, P[i] >= P[i+1]); end
        for blk in blocks; @constraint(m, sum(P[i] for i in blk) <= 1.0); end
        if lam == :p1; @constraint(m, P[1] >= P[4] + P[5])
        else;          @constraint(m, P[4] + P[5] >= P[1]); end
        load = [AffExpr(0.0) for _ in 1:4]
        for j in 1:min(4, n); load[j] += P[j]; end
        τ = RHOA * (lam == :p1 ? P[1] : P[4] + P[5])
        for j in 5:n
            pre = copy(load); a = assign[j]; Ej = Esets[j]
            for mm in 1:4
                if mm in Ej; @constraint(m, pre[mm] + P[j] <= τ)
                else;        @constraint(m, pre[mm] + P[j] >= τ); end
            end
            if isempty(Ej); for mm in 1:4; @constraint(m, pre[a] <= pre[mm]); end
            else;           for mm in Ej;   @constraint(m, pre[a] >= pre[mm]); end; end
            load[a] += P[j]
        end
        for mm in 1:4; @constraint(m, load[am] >= load[mm]); end
        @objective(m, Max, load[am]); optimize!(m)
        if termination_status(m) == OPTIMAL && objective_value(m) > best + 1e-12
            best = objective_value(m); bp = value.(P)
        end
    end
    return best, bp, (assign, branch, lam, am)
end

# ---------- Step A：采样 + 去重 ----------
"整数格点/半格点家族：最坏实例看起来都长这样"
function grid_instance(n, rng; den = 10)
    p = Float64[max(rand(rng, 1:den), 1) / den for _ in 1:n]
    sort!(p; rev = true); return p
end

function main()
    rng = MersenneTwister(20260930)
    groups = Dict{String, Tuple{Float64, Vector{Float64}, Any}}()   # key → (best ratio, p, trace)
    n_samp = 0
    for n in 7:12, trial in 1:4000
        fam = rand(rng, (:grid10, :grid20, :grid5, :pow, :blocks, :general))
        p = fam == :grid10 ? grid_instance(n, rng; den = 10) :
            fam == :grid20 ? grid_instance(n, rng; den = 20) :
            fam == :grid5  ? grid_instance(n, rng; den = 5)  :
            gen_instance(n, rng; family = fam, lower = rand(rng) < 0.5 ? ALPHA + 1e-9 : 0.0)
        n_samp += 1
        r = a4_sim(p, A4(C_TARGET, [:p1, :p45], false, false))[1] / opt_makespan(p, 4)
        r < 1.10 && continue                              # 只留下接近最坏的
        tr = a4c_trace(p); k = keyof(tr)
        if !haskey(groups, k) || r > groups[k][1]
            groups[k] = (r, copy(p), tr)
        end
    end
    println("采样 ", n_samp, " 个实例（比值 ≥1.10 者按轨迹去重）→ 轨迹数 ", length(groups))
    # 取比值最高的 40 条轨迹
    items = collect(values(groups)); sort!(items; by = x -> -x[1])
    sel = items[1:min(40, length(items))]
    println("对前 ", length(sel), " 条轨迹跑 LP 天花板（每条 10–25 s）\n")
    best = 0.0; best_p = Float64[]; best_tr = nothing
    for (i, (r, p, tr)) in enumerate(sel)
        t0 = time()
        c, cp, ctr = ceiling(p)
        flag = c > 1.2 + 1e-9 ? "  ✗ > 6/5" : (abs(c - 1.2) < 1e-9 ? "  = 6/5（紧）" : "")
        println(lpad(i, 3), "  采样比值 ", rpad(round(r, digits = 5), 8), " 片内天花板 ",
                rpad(round(c, digits = 6), 10), "(", round(time() - t0, digits = 0), "s)", flag)
        if c > best
            best = c; best_p = cp; best_tr = ctr
            c > 1.2 + 1e-9 && println("         ⚠ 反例见证 p = ", round.(cp, digits = 4))
        end
    end
    println("\n", "="^80)
    println("扫描到的最大的片内天花板 = ", round(best, digits = 6),
            "  = ", round(best / C_TARGET, digits = 4), "×c ； ", round(best / 1.25, digits = 4), "×(5/4)")
    println("见证 p = ", round.(best_p, digits = 4), "（C* = ", round(opt_makespan(best_p, 4), digits = 6), "）")
    println("该实例上 A4c 比值（直接仿真）= ",
            round(a4_sim(best_p, A4(C_TARGET, [:p1, :p45], false, false))[1] / opt_makespan(best_p, 4), digits = 6))
end

main()
