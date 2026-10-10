include("a4_lib.jl")
using JuMP, HiGHS
const RHO2 = C_TARGET
function a4c_trace2(p)
    n = length(p); load = zeros(4); assign = zeros(Int,n); branch = fill(:open,n)
    Esets = [Int[] for _ in 1:n]
    for j in 1:min(4,n); assign[j]=j; load[j]+=p[j]; end
    n<=4 && return (assign, branch, :none, argmax(load), maximum(load), Esets)
    Λ1 = p[1]; Λ2 = p[4]+p[5]; lam = Λ2 > Λ1 ? :p45 : :p1
    τ = RHO2*max(Λ1,Λ2)
    for j in 5:n
        E = [m for m in 1:4 if load[m]+p[j] <= τ+1e-15]
        Esets[j] = copy(E)
        if isempty(E); assign[j]=argmin(load); branch[j]=:fb
        else; assign[j]=E[argmax(load[E])]; branch[j]=:E; end
        load[assign[j]] += p[j]
    end
    return (assign, branch, lam, argmax(load), maximum(load), Esets)
end
function ceiling(p0; rho=RHO2)
    cstar = opt_makespan(p0,4); p = p0 ./ cstar
    assign, branch, lam, am, ms, Esets = a4c_trace2(p)
    best = -Inf; bp = Float64[]
    for blocks in partitions(length(p), 3, 4)
        m = Model(HiGHS.Optimizer); set_silent(m)
        @variable(m, P[1:length(p)] >= 0)
        for i in 1:(length(p)-1); @constraint(m, P[i] >= P[i+1]); end
        for blk in blocks; @constraint(m, sum(P[i] for i in blk) <= 1.0); end
        if lam == :p1; @constraint(m, P[1] >= P[4]+P[5]); else; @constraint(m, P[4]+P[5] >= P[1]); end
        load = [AffExpr(0.0) for _ in 1:4]
        for j in 1:min(4,length(p)); load[j] += P[j]; end
        τ = rho * (lam == :p1 ? P[1] : P[4]+P[5])
        for j in 5:length(p)
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
    return best, bp
end
# 起点：攻击的 5 个 seed 见证 + LP 上一轮给出的干净实例
starts = [
 [0.7759,0.6534,0.6534,0.5212,0.5184,0.5184,0.3966,0.3957,0.3932,0.3908],
 [0.8183,0.6837,0.6837,0.5471,0.5428,0.5411,0.4152,0.4152,0.413,0.413],
 [0.8917,0.7481,0.742,0.5774,0.5679,0.5649,0.4595,0.4594,0.4593,0.459],
 [1.2066,1.0184,1.0055,0.8181,0.8178,0.8122,0.613,0.609,0.5991,0.5961],
 [0.6,0.5,0.5,0.4,0.4,0.4,0.3,0.3,0.3,0.3],
]
println("轨迹跳跃搜索（每次 = 片内 LP 精确上确界）")
println(rpad("起点/迭代", 12), lpad("片内天花板", 12), "   见证 p")
function hop()
    best_all = 0.0; best_p = Float64[]
    for (i, s) in enumerate(starts)
        c, p = ceiling(s)
        println(rpad("start $i", 12), lpad(round(c, digits = 6), 12), "   ", round.(p, digits = 4))
        c > best_all && (best_all = c; best_p = copy(p))
    end
    # 从最优处再跳两轮
    for it in 1:3
        c, p = ceiling(best_p ./ opt_makespan(best_p, 4))
        println(rpad("hop $it", 12), lpad(round(c, digits = 6), 12), "   ", round.(p, digits = 4))
        if c > best_all + 1e-9
            best_all = c; best_p = copy(p)
        else
            break
        end
    end
    println("-"^84)
    println("找到的最大片内天花板 = ", round(best_all, digits = 6),
            "   = ", round(best_all/C_TARGET, digits = 4), "×c ；", round(best_all/1.25, digits = 4), "×(5/4)")
    println("对应实例 p = ", round.(best_p, digits = 4), "   (C* = ", round(opt_makespan(best_p,4), digits = 6), ")")
    println("直接仿真 A4c 比值 = ", round(a4_sim(best_p, A4(C_TARGET, [:p1,:p45], false, false))[1]/opt_makespan(best_p,4), digits = 6))

end
hop()
