# a4_l3_lpcuts.jl —— 层 (3) 逐片「轨迹 + 纯 LP 装箱割」天花板可行性探针
#   若 LP+割 的片天花板全部 ≤ 6/5，则层 (3) 可发 1210×4 张精确有理证书（复用 razor 管线）
using JuMP, HiGHS
include("a4_lib.jl")
include("a4_milp10.jl")

"纯 LP 片天花板：轨迹约束 + 合法装箱割（无二元）；4 台机各求一次 sup 取最大"
function lp_ceiling(k, masks; preds)
    n = 4 + length(k)
    best = -Inf
    for mm in 1:4
        m = Model(HiGHS.Optimizer); set_silent(m)
        @variable(m, P[1:n])
        for i in 1:n; set_lower_bound(P[i], ALP); set_upper_bound(P[i], 1.0); end
        for i in 1:(n-1); @constraint(m, P[i] >= P[i+1]); end
        preds == :full1 ? @constraint(m, P[1] >= P[4] + P[5]) : @constraint(m, P[4] + P[5] >= P[1])
        @constraint(m, sum(P) <= 4.0)
        # 普适合法装箱割（n=9）
        @constraint(m, P[4] + P[5] <= 1)
        @constraint(m, P[5] + P[6] <= 1)
        @constraint(m, P[7] + P[8] + P[9] <= 1)
        ℓ = _trace!(m, P, k, masks; n = n, preds = preds)
        @objective(m, Max, ℓ[mm])
        optimize!(m)
        termination_status(m) == OPTIMAL || return NaN
        best = max(best, objective_value(m))
    end
    return best
end

function load_pieces(file)
    out = Tuple{Vector{Int}, Vector{Int}}[]
    for line in eachline(file)
        isempty(strip(line)) && continue
        v = parse.(Int, split(line)); h = length(v) ÷ 2
        push!(out, (v[1:h], v[(h+1):end]))
    end
    return out
end

function pre_z_counts(k)
    c = ones(Int, 4)
    for j in 1:(length(k)-1); c[k[j]] += 1; end
    return sort(c, rev = true)
end

function main()
    for (file, preds) in (("fam9_leaves_p45.txt", :full45), ("fam9_leaves_p1.txt", :full1))
        pieces = load_pieces(file)
        sel = filter(p -> p[2][end] == 0 && pre_z_counts(p[1]) == [2, 2, 2, 2], pieces)
        println("== $(file)：命中 $(length(sel)) 片")
        # 采样 40 条 + 必含 razor 片（若在）
        razor = ([1, 2, 3, 4, 3], [15, 14, 12, 8, 0])
        sample = sel[round.(Int, range(1, length(sel), length = min(40, length(sel))))]
        razor in sel && push!(sample, razor)
        worst = -Inf; wp = nothing; nbeyond = 0
        for (k, masks) in sample
            v = lp_ceiling(k, masks; preds = preds)
            isnan(v) && continue
            v > worst && (worst = v; wp = (k, masks))
            v > 6 / 5 + 1e-9 && (nbeyond += 1; println("  LP+割 超 6/5：$(round(v, digits=6))  k=$k masks=$masks"))
        end
        println("  采样最大 LP+割天花板 = $(round(worst, digits=6)) @ $(wp)；超 6/5 的 $(nbeyond) 条")
        flush(stdout)
    end
end

main()
