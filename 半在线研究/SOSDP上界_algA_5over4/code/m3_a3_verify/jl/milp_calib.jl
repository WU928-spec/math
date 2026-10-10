# milp_calib.jl —— 校准实验：把"存在装箱"用二值变量+big-M 合成一个 MILP，测单次成本
include("a4_lib.jl")
using JuMP, HiGHS
const RHO = C_TARGET

function trace8(p)
    n = length(p); load = zeros(4); assign = zeros(Int,n); Esets = [Int[] for _ in 1:n]
    for j in 1:min(4,n); assign[j]=j; load[j]+=p[j]; end
    lam = (p[4]+p[5] > p[1]) ? :p45 : :p1
    τ = RHO*max(p[1], p[4]+p[5])
    for j in 5:n
        E = [m for m in 1:4 if load[m]+p[j] <= τ+1e-15]; Esets[j]=copy(E)
        assign[j] = isempty(E) ? argmin(load) : E[argmax(load[E])]
        load[assign[j]] += p[j]
    end
    return assign, Esets, lam, argmax(load)
end

"MILP 天花板：轨迹固定，装箱用 x/y 二值+big-M 合成"
function milp_ceiling(p0)
    cstar = opt_makespan(p0,4); p0 = p0 ./ cstar
    assign, Esets, lam, am = trace8(p0); n = length(p0)
    m = Model(HiGHS.Optimizer); set_silent(m)
    set_optimizer_attribute(m, "time_limit", 60.0)
    @variable(m, 0 <= P[1:n] <= 1)
    for i in 1:(n-1); @constraint(m, P[i] >= P[i+1]); end
    @variable(m, x[1:n,1:4], Bin)
    @variable(m, y[1:n,1:4] >= 0)
    for i in 1:n
        @constraint(m, sum(x[i,mm] for mm in 1:4) == 1)
        for mm in 1:4
            @constraint(m, y[i,mm] <= x[i,mm])
            @constraint(m, y[i,mm] <= P[i])
            @constraint(m, y[i,mm] >= P[i] - (1 - x[i,mm]))
        end
    end
    for mm in 1:4; @constraint(m, sum(y[i,mm] for i in 1:n) <= 1.0); end
    lam == :p1 ? @constraint(m, P[1] >= P[4]+P[5]) : @constraint(m, P[4]+P[5] >= P[1])
    load = [AffExpr(0.0) for _ in 1:4]
    for j in 1:min(4,n); load[j] += P[j]; end
    τ = RHO * (lam == :p1 ? P[1] : P[4]+P[5])
    for j in 5:n
        pre = copy(load); a = assign[j]; Ej = Esets[j]
        for mm in 1:4
            mm in Ej ? @constraint(m, pre[mm] + P[j] <= τ) : @constraint(m, pre[mm] + P[j] >= τ)
        end
        if isempty(Ej); for mm in 1:4; @constraint(m, pre[a] <= pre[mm]); end
        else;           for mm in Ej;   @constraint(m, pre[a] >= pre[mm]); end; end
        load[a] += P[j]
    end
    for mm in 1:4; @constraint(m, load[am] >= load[mm]); end
    @objective(m, Max, load[am])
    t0 = time(); optimize!(m); el = time() - t0
    return termination_status(m), (is_solved_and_feasible(m) ? objective_value(m) : NaN), el, n
end

w = [0.6,0.5,0.5,0.4,0.4,0.4,0.3,0.3,0.3,0.3]
st, val, el, n = milp_ceiling(w)
println("n=10, 1 个 MILP：状态=", st, "  天花板=", round(val, digits = 6), "  时间=", round(el, digits = 3), " s")
for (k, p) in enumerate([[0.7759,0.6534,0.6534,0.5212,0.5184,0.5184,0.3966,0.3957,0.3932,0.3908],
                         [0.8195,0.8195,0.8195,0.6391,0.3609,0.1805,0.1805,0.0,0.0],
                         [0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5]])
    st, val, el, n = milp_ceiling(p)
    println("n=", n, " 第 ", k, " 个：状态=", st, "  天花板=", round(val, digits = 6), "  时间=", round(el, digits = 3), " s")
end
