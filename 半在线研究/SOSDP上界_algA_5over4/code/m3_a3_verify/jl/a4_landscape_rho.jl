# ρ 版全形状终态封顶地图（H5i 引理 M_ρ 的形状分类）
# 与 a4_landscape.jl 的差异（失败区常数全换）：件下界 α₀=4(ρ−1)/3=0.24061（原 4/15）、
# 箱件数上限 4（原 3；因 4α₀<1 使 4-件箱存活）、n=6..13（引理 A 限每机 ≤3 件 ⟹ n−1≤12）。
# 输出：每个有序计数形状的终端 sup(min_pre+z)；按 ρ 分类（<ρ 闭合 / =ρ razor 级 / >ρ 伪见证）。
using JuMP, HiGHS, Printf

const RHO = (1 + sqrt(37)) / 6
const ALPHA0 = 4 * (RHO - 1) / 3      # = 0.24061...

function layer_ceiling(n, cnt; zcap = 1 / 3, tlim = 90.0)
    m = Model(HiGHS.Optimizer); set_silent(m); set_time_limit_sec(m, tlim)
    @variable(m, P[1:n])
    for i in 1:n; set_lower_bound(P[i], ALPHA0); set_upper_bound(P[i], 1.0); end
    for i in 1:(n - 1); @constraint(m, P[i] >= P[i+1]); end
    @constraint(m, sum(P) <= 4.0)
    @constraint(m, P[n] <= zcap)
    @variable(m, u[1:(n-1), 1:4], Bin)
    @variable(m, v[1:(n-1), 1:4] >= 0)
    for i in 1:(n-1)
        @constraint(m, sum(u[i, :]) == 1)
        for mm in 1:4
            @constraint(m, v[i, mm] <= u[i, mm])
            @constraint(m, v[i, mm] <= P[i])
            @constraint(m, v[i, mm] >= P[i] - (1 - u[i, mm]))
        end
    end
    for mm in 1:4
        @constraint(m, u[mm, mm] == 1)
        @constraint(m, sum(u[:, mm]) == cnt[mm])
    end
    ℓ = [sum(v[:, mm]) for mm in 1:4]
    @variable(m, x[1:n, 1:4], Bin)
    @variable(m, y[1:n, 1:4] >= 0)
    for i in 1:n
        @constraint(m, sum(x[i, :]) == 1)
        for b in 1:4
            @constraint(m, y[i, b] <= x[i, b])
            @constraint(m, y[i, b] <= P[i])
            @constraint(m, y[i, b] >= P[i] - (1 - x[i, b]))
        end
    end
    for b in 1:4
        @constraint(m, sum(y[:, b]) <= 1.0)
        @constraint(m, sum(x[:, b]) <= 4)       # ρ 版：箱至多 4 件
    end
    @constraint(m, x[1, 1] == 1)
    @variable(m, t)
    for mm in 1:4; @constraint(m, t <= ℓ[mm] + P[n]); end
    @objective(m, Max, t)
    optimize!(m)
    st = termination_status(m)
    if st == OPTIMAL
        return objective_value(m), "OPT"
    elseif primal_status(m) == FEASIBLE_POINT
        return objective_value(m), "TIMELIMIT"
    else
        return NaN, string(st)
    end
end

function count_vectors(n)
    out = Vector{Int}[]
    for c1 in 1:3, c2 in 1:3, c3 in 1:3, c4 in 1:3
        c1 + c2 + c3 + c4 == n - 1 && push!(out, [c1, c2, c3, c4])
    end
    out
end

function main()
    println("ρ 版全形状地图：α₀=$(round(ALPHA0, digits=5))，ρ=$(round(RHO, digits=6))"); flush(stdout)
    allres = Tuple{Float64,Int,Vector{Int},String}[]
    for n in 6:13
        cvs = count_vectors(n)
        t0 = time()
        for cnt in cvs
            v, st = layer_ceiling(n, cnt)
            push!(allres, (v, n, cnt, st))
            @printf("n=%2d cnt=%s : %s\n", n, string(cnt), isnan(v) ? st : string(round(v, digits=6)))
            flush(stdout)
        end
        @printf("== n=%d 完成（%d 形状，%.0fs）==\n", n, length(cvs), time() - t0); flush(stdout)
    end
    println("\n=== 总分类（按 sup vs ρ）===")
    nclosed = nrazor = npseudo = 0
    sort!(allres; by = r -> isnan(r[1]) ? -Inf : r[1], rev = true)
    for (v, n, cnt, st) in allres
        if isnan(v)
            println("  NaN  n=$n cnt=$cnt  $st"); continue
        end
        if v > RHO + 1e-4
            npseudo += 1; @printf("  ✗ 超ρ   %.6f  n=%2d cnt=%s\n", v, n, string(cnt))
        elseif v > RHO - 1e-4
            nrazor += 1;  @printf("  =ρ边  %.6f  n=%2d cnt=%s\n", v, n, string(cnt))
        else
            nclosed += 1
        end
    end
    @printf("汇总：闭合 %d / ρ 边界 %d / 伪见证 %d / 总 %d\n", nclosed, nrazor, npseudo, length(allres))
end
main()
