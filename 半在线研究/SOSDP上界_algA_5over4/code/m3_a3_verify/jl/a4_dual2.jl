# a4_dual2.jl —— 对分支 A 的紧片抽对偶证书（自动找最优装箱、固定、取对偶权重）
#   用法：julia --project=. a4_dual2.jl "<a5..a10>" "<mask5..mask10>"
include("a4_lib.jl")
include("a4_milp10.jl")
using JuMP, HiGHS

"先求该片天花板下的最优 p 与装箱；固定装箱后转纯 LP 并抽对偶"
function dual_of(k::Vector{Int}, masks::Vector{Int})
    n = 4 + length(k)
    # ① 求天花板（找到最优 p 与最优装箱）
    best = -Inf; bp = Float64[]; bx = nothing
    for mm in 1:4
        m, P = _base(n; preds = :card); set_silent(m)
        ℓ = _trace!(m, P, k, masks; n = n, preds = :card)
        for m2 in 1:4; m2 == mm && continue; @constraint(m, ℓ[mm] >= ℓ[m2]); end
        @objective(m, Max, ℓ[mm]); optimize!(m)
        if termination_status(m) == OPTIMAL && objective_value(m) > best
            best = objective_value(m); bp = value.(P); bx = value.(m[:x])
        end
    end
    isnan(best) && return println("片不可行")
    println("天花板 = ", round(best, digits = 8), "  最优 p = ", round.(bp, digits = 4))
    # ② 固定 p 与装箱，转纯 LP，抽对偶
    m = Model(HiGHS.Optimizer); set_silent(m)
    @variable(m, P[1:n])
    refs = Dict{String,Any}()
    for i in 1:n; set_lower_bound(P[i], ALP); set_upper_bound(P[i], 1.0); refs["lo$i"] = @constraint(m, P[i] >= ALP); end
    for i in 1:(n-1); refs["mon$i"] = @constraint(m, P[i] >= P[i+1]); end
    # 装箱：由最优 x 反推每个箱的元素集合
    bins = [Int[] for _ in 1:4]
    for i in 1:n, b in 1:4
        bx[i, b] > 0.5 && push!(bins[b], i)
    end
    for (bi, blk) in enumerate(bins)
        isempty(blk) && continue
        refs["bin$bi"] = @constraint(m, sum(P[i] for i in blk) <= 1.0)
    end
    refs["f1"] = @constraint(m, P[4] + P[5] >= P[1])
    refs["f2"] = @constraint(m, P[2] <= P[3] + P[4])
    refs["f3"] = @constraint(m, P[3] <= P[4] + P[5])
    refs["f4"] = @constraint(m, P[5] <= P[3])
    refs["sum"] = @constraint(m, sum(P) <= 4.0)
    # 轨迹约束（同临界片）
    τ = RHO * (P[4] + P[5])
    ℓ = [AffExpr(0.0) for _ in 1:4]; for mm in 1:4; ℓ[mm] += P[mm]; end
    for c in 1:length(k)
        j = 4 + c; Ej = [mm for mm in 1:4 if (masks[c] >> (mm - 1)) & 1 == 1]; aj = k[c]
        pre = copy(ℓ)
        for mm in 1:4
            if mm in Ej; refs["E$c.$mm"] = @constraint(m, pre[mm] + P[j] <= τ)
            else;            refs["E$c.$mm"] = @constraint(m, pre[mm] + P[j] >= τ); end
        end
        if isempty(Ej)
            for mm in 1:4; mm == aj && continue; refs["a$c.$mm"] = @constraint(m, pre[aj] <= pre[mm]); end
        else
            for mm in Ej; mm == aj && continue; refs["a$c.$mm"] = @constraint(m, pre[aj] >= pre[mm]); end
        end
        ℓ[aj] += P[j]
    end
    am = argmax([sum(bp[i] for i in findall(==(mm), k)) + (mm <= 4 ? bp[mm] : 0.0) for mm in 1:4])
    for mm in 1:4; mm == am && continue; refs["h$mm"] = @constraint(m, ℓ[am] >= ℓ[mm]); end
    @objective(m, Max, ℓ[am]); optimize!(m)
    println("对偶权重（非零）：")
    for (kk, r) in sort(collect(refs); by = x -> x[1])
        d = dual(r); abs(d) > 1e-9 && println("   ", rpad(kk, 8), " → ", round(d, digits = 5))
    end
end

dual_of(parse.(Int, split(ARGS[1])), parse.(Int, split(ARGS[2])))
