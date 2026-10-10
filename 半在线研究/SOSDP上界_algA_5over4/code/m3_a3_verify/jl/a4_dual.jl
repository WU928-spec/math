# a4_dual.jl —— 对临界片（固定最优装箱后是纯 LP）抽对偶证书
#   临界实例 p*=(0.6,0.5,0.5,0.4,0.4,0.4,0.3,0.3,0.3,0.3)，C*=1，最优装箱：
#     bin1={1,5} bin2={2,3} bin3={4,7,8} bin4={6,9,10}
#   临界轨迹 a=(2,3,1,4,4,1), E=(14,12,9,8,0,0)。目标：max ℓ_1（最重机）
#   对偶权重 = 把约束组合成"ℓ_1 ≤ 1.2"的证明权重，正是势函数的影子。
include("a4_lib.jl")
using JuMP, HiGHS

const RHO = C_TARGET
const ALP = 4.0 / 15.0

function dual_of_critical()
    n = 10
    m = Model(HiGHS.Optimizer); set_silent(m)
    @variable(m, P[1:n])
    refs = Dict{String,Any}()
    for i in 1:n; refs["lo$i"] = @constraint(m, P[i] >= ALP); end
    for i in 1:(n-1); refs["mon$i"] = @constraint(m, P[i] >= P[i+1]); end
    # 固定装箱（= 临界实例的最优装箱）
    for (bi, blk) in enumerate([[1,5],[2,3],[4,7,8],[6,9,10]])
        refs["bin$bi"] = @constraint(m, sum(P[i] for i in blk) <= 1.0)
    end
    # 家族谓词
    refs["f1"] = @constraint(m, P[4] + P[5] >= P[1])
    refs["f2"] = @constraint(m, P[2] <= P[3] + P[4])
    refs["f3"] = @constraint(m, P[3] <= P[4] + P[5])
    refs["f4"] = @constraint(m, P[5] <= P[3])
    refs["sum"] = @constraint(m, sum(P) <= 4.0)
    # 轨迹约束（临界片）
    k = [2,3,1,4,4,1]; masks = [14,12,9,8,0,0]
    τ = RHO * (P[4] + P[5])
    ℓ = [AffExpr(0.0) for _ in 1:4]
    for mm in 1:4; ℓ[mm] += P[mm]; end
    for c in 1:6
        j = 4 + c
        Ej = [mm for mm in 1:4 if (masks[c] >> (mm - 1)) & 1 == 1]
        aj = k[c]
        pre = copy(ℓ)
        for mm in 1:4
            sgn = mm in Ej ? :le : :ge
            if sgn == :le; refs["E$c.$mm"] = @constraint(m, pre[mm] + P[j] <= τ)
            else;            refs["E$c.$mm"] = @constraint(m, pre[mm] + P[j] >= τ); end
        end
        if isempty(Ej)
            for mm in 1:4; mm == aj && continue; refs["a$c.$mm"] = @constraint(m, pre[aj] <= pre[mm]); end
        else
            for mm in Ej; mm == aj && continue; refs["a$c.$mm"] = @constraint(m, pre[aj] >= pre[mm]); end
        end
        ℓ[aj] += P[j]
    end
    for mm in 1:4; mm == 1 && continue; refs["h$mm"] = @constraint(m, ℓ[1] >= ℓ[mm]); end
    @objective(m, Max, ℓ[1])
    optimize!(m)
    println("最优值 = ", round(objective_value(m), digits = 8))
    println("各约束的对偶权重（非零的）：")
    for (k, r) in sort(collect(refs); by = x -> x[1])
        d = dual(r)
        abs(d) > 1e-9 && println("   ", rpad(k, 8), " → ", round(d, digits = 5))
    end
end
dual_of_critical()
