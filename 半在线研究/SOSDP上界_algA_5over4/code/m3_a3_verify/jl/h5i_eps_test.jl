#  ε-内缩测试：片 k=2,4,3,1,1 masks=14,12,5,1,0 (L) 的 sup=1.1858 是否可从严格内部逼近？
#  所有"不合格"约束加 ε 边距（pre+Pj ≥ τ+ε），合格侧 ≤τ 不动（闭侧本就正确）；ε→0 看 sup 走向
include("a4_lib.jl")
using JuMP, HiGHS, Printf

const RHO = C_TARGET
const ALP0 = 4 * (RHO - 1) / 3
const BIGM = 6.0
eset(mask::Int) = [mm for mm in 1:4 if (mask >> (mm - 1)) & 1 == 1]

function leaf_eps(n, k, masks, mode, eps)
    m = Model(HiGHS.Optimizer); set_silent(m); set_time_limit_sec(m, 120.0)
    @variable(m, ALP0 <= P[1:n] <= 1.0)
    for i in 1:(n - 1); @constraint(m, P[i] >= P[i + 1]); end
    @constraint(m, P[n] <= 1 / 3)
    @constraint(m, sum(P) <= 4.0)
    @variable(m, x[1:n, 1:4], Bin)
    @variable(m, y[1:n, 1:4] >= 0)
    for i in 1:n
        @constraint(m, sum(x[i, :]) == 1)
        for b in 1:4
            @constraint(m, y[i, b] <= x[i, b]); @constraint(m, y[i, b] <= P[i])
            @constraint(m, y[i, b] >= P[i] - (1 - x[i, b]))
        end
    end
    for b in 1:4
        @constraint(m, sum(y[:, b]) <= 1.0)
        @constraint(m, sum(x[:, b]) <= 4)
    end
    @constraint(m, x[1, 1] == 1)
    @variable(m, lam >= 0)
    @variable(m, blam, Bin)
    @constraint(m, lam >= P[1])
    @constraint(m, lam >= P[4] + P[5])
    @constraint(m, lam <= P[1] + BIGM * blam)
    @constraint(m, lam <= P[4] + P[5] + BIGM * (1 - blam))
    τ = RHO * lam
    ℓ = [AffExpr(0.0) for _ in 1:4]
    for mm in 1:4; ℓ[mm] += P[mm]; end
    for c in 1:(n - 4)
        j = 4 + c; E = eset(masks[c]); a = k[c]
        pre = copy(ℓ)
        if j < n
            for mm in 1:4
                if mm in E; @constraint(m, pre[mm] + P[j] <= τ)
                else;       @constraint(m, pre[mm] + P[j] >= τ + eps); end
            end
            if isempty(E)
                for mm in 1:4; @constraint(m, pre[a] <= pre[mm]); end
            elseif mode == :F || j == 5
                for mm in E; @constraint(m, pre[a] >= pre[mm]); end
            else
                for mm in E; @constraint(m, pre[a] <= pre[mm]); end
            end
        else
            for mm in 1:4
                @constraint(m, pre[mm] + P[j] >= τ + eps)
                @constraint(m, pre[a] <= pre[mm])
            end
        end
        ℓ[a] += P[j]
    end
    r = k[n - 4]
    @objective(m, Max, ℓ[r])
    optimize!(m)
    st = termination_status(m)
    return (st == OPTIMAL) ? objective_value(m) : NaN, (st == OPTIMAL ? value.(P) : Float64[])
end

function main()
    k = [2, 4, 3, 1, 1]; masks = [14, 12, 5, 1, 0]
    for eps in [0.0, 0.001, 0.005, 0.01, 0.02, 0.04]
        v, p = leaf_eps(9, k, masks, :L, eps)
        @printf("ε=%.3f  sup=%s  p*=%s\n", eps, isnan(v) ? "不可行" : string(round(v, digits = 8)),
                isempty(p) ? "-" : string(round.(p; digits = 4)))
        flush(stdout)
    end
end
main()
