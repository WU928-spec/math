# a4_razor_pure_lp.jl —— razor 形状 [2,2,2,3]：固定 60 种机指派，纯 LP + 合法装箱割，sup(min+z) 测试
#   目的：判断"精确有理 Farkas 证书"路线是否可行（老项目方法：固定骨架 → 纯 LP → Fraction 验证对偶）
#   合法性论证见记录 §3i。H（形状内 min+z>6/5 ⟺ 四机全 >6/5−z）以 ≥ 加入，sup 不变。
using JuMP, HiGHS

const PERMS3 = [[1,2,3],[1,3,2],[2,1,3],[2,3,1],[3,1,2],[3,2,1]]

function lp_sup(assign::Vector{Vector{Int}})
    # assign[m] = 机 m 的工件下标列表（含初始件 m）
    n = 10
    m = Model(HiGHS.Optimizer); set_silent(m)
    @variable(m, 4 / 15 <= P[1:n] <= 1.0)
    for i in 1:(n-1); @constraint(m, P[i] >= P[i+1]); end
    @constraint(m, sum(P) <= 4.0)
    @constraint(m, P[n] <= 1 / 3)
    # 合法装箱割（普适有效，不依赖轨迹）
    @constraint(m, P[4] + P[5] <= 1)
    @constraint(m, P[5] + P[6] <= 1)
    @constraint(m, P[7] + P[8] + P[9] <= 1)
    @constraint(m, P[8] + P[9] + P[10] <= 1)
    ℓ = [sum(P[i] for i in assign[mm]) for mm in 1:4]
    # H：四机负载 ≥ 6/5 − z（sup 语义等价，见上）
    for mm in 1:4; @constraint(m, ℓ[mm] >= 6 / 5 - P[n]); end
    @variable(m, t)
    for mm in 1:4; @constraint(m, t <= ℓ[mm] + P[n]); end
    @objective(m, Max, t)
    optimize!(m)
    st = termination_status(m)
    st == OPTIMAL || return (NaN, Float64[], st)
    return objective_value(m), value.(P), st
end

function main()
    # razor 序 [2,2,2,3]：机 4 拿后续件中的 2 件，机 1..3 各拿 1 件（共 5 件：5..9）
    nbad = 0; ntot = 0; worst = -Inf; worsta = nothing
    for a in 5:9, b in (a+1):9
        rest = setdiff(5:9, [a, b])
        for pm in PERMS3
            assign = [[1, rest[pm[1]]], [2, rest[pm[2]]], [3, rest[pm[3]]], [4, a, b]]
            v, pv, st = lp_sup(assign)
            ntot += 1
            if isnan(v); continue; end
            if v > worst; worst = v; worsta = assign; end
            if v > 1.2 + 1e-9
                nbad += 1
                println("超 6/5：assign=$assign sup=$(round(v, digits=6))  p=", round.(pv, digits = 4))
            end
        end
    end
    println("\n共 $ntot 种机指派；sup>6/5 的有 $nbad 种；最大 sup = $(round(worst, digits=8)) @ $worsta")
end

main()
