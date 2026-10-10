# a4_feat2.jl —— （修正版）片天花板 + 特征提取；实例一律排序、且满足 α' 下界（目标 ρ=1.2 的反例设定）
include("a4_lib.jl")
using JuMP, HiGHS
const RHO = C_TARGET
const RHO_T = 1.2
const ALP = (RHO_T - 1) * 4 / 3        # = 0.266666...：反例中所有工件 > α'
function tr(p)
    n=length(p); load=zeros(4); a=zeros(Int,n); E=[Int[] for _ in 1:n]
    for j in 1:min(4,n); a[j]=j; load[j]+=p[j]; end
    lam = (p[4]+p[5] > p[1]) ? :p45 : :p1
    τ = RHO*max(p[1],p[4]+p[5])
    for j in 5:n
        Ej=[m for m in 1:4 if load[m]+p[j] <= τ+1e-15]; E[j]=copy(Ej)
        a[j] = isempty(Ej) ? argmin(load) : Ej[argmax(load[Ej])]
        load[a[j]] += p[j]
    end
    return a,E,lam,argmax(load)
end
key(p) = (t=tr(p); string(length(p),"|",t[1],"|",t[2],"|",t[3],"|",t[4]))
function ceil_lp(p0)
    p = p0 ./ opt_makespan(p0,4); n=length(p); a,E,lam,am = tr(p)
    best=-Inf; bp=Float64[]
    for blocks in partitions(n,3,4)
        m=Model(HiGHS.Optimizer); set_silent(m)
        @variable(m, P[1:n])
        for i in 1:n; set_lower_bound(P[i], ALP); end
        for i in 1:(n-1); @constraint(m, P[i] >= P[i+1]); end
        for blk in blocks; @constraint(m, sum(P[i] for i in blk) <= 1.0); end
        lam == :p1 ? @constraint(m, P[1] >= P[4]+P[5]) : @constraint(m, P[4]+P[5] >= P[1])
        load=[AffExpr(0.0) for _ in 1:4]; for j in 1:min(4,n); load[j]+=P[j]; end
        τ = RHO*(lam==:p1 ? P[1] : P[4]+P[5])
        for j in 5:n
            pre=copy(load); aa=a[j]; Ej=E[j]
            for mm in 1:4
                mm in Ej ? @constraint(m, pre[mm]+P[j] <= τ) : @constraint(m, pre[mm]+P[j] >= τ)
            end
            if isempty(Ej); for mm in 1:4; @constraint(m, pre[aa] <= pre[mm]); end
            else; for mm in Ej; @constraint(m, pre[aa] >= pre[mm]); end; end
            load[aa] += P[j]
        end
        for mm in 1:4; @constraint(m, load[am] >= load[mm]); end
        @objective(m, Max, load[am]); optimize!(m)
        if termination_status(m)==OPTIMAL && objective_value(m) > best+1e-12
            best=objective_value(m); bp=value.(P)
        end
    end
    return best, bp, (a,E,lam,am)
end
function feats(p,a,E,lam)
    n=length(p)
    return Dict("n"=>n, "lam"=>string(lam), "nE"=>count(j->!isempty(E[j]),5:n),
                "nFB"=>count(j->isempty(E[j]),5:n), "prof"=>[count(==(mm),a) for mm in 1:4],
                "p1≥p45"=>p[1]>=p[4]+p[5], "p3≥p45"=>p[3]>=p[4]+p[5], "p2≥p3+p4"=>p[2]>=p[3]+p[4],
                "p5≥p3"=>p[5]>=p[3], "p4+p5≥p2"=>p[4]+p[5]>=p[2])
end
function main()
    rng=MersenneTwister(11); seen=Set{String}(); rows=[]
    for n in 9:12, _ in 1:8000
        p = rand(rng) < 0.6 ? sort(Float64[rand(rng,1:10)/10 for _ in 1:n]; rev=true) :
                              sort(Float64[ALP + rand(rng)*(1-ALP) for _ in 1:n]; rev=true)
        k = key(p); k in seen && continue
        r = a4_sim(p, A4(C_TARGET,[:p1,:p45],false,false))[1]/opt_makespan(p,4)
        r < 1.15 && continue
        push!(seen,k)
        c, cp, (a,E,lam,am) = ceil_lp(p)
        push!(rows,(r,c,cp,feats(cp,a,E,lam)))
        println("片 ", lpad(length(rows),2), " n=", n, " 采样 ", rpad(round(r,digits=4),7),
                " 天花板 ", rpad(round(c,digits=6),9), " Λ=", lam, " E步=", feats(cp,a,E,lam)["nE"],
                " 兜底=", feats(cp,a,E,lam)["nFB"], " prof=", feats(cp,a,E,lam)["prof"],
                " | p2≥p3+p4:", feats(cp,a,E,lam)["p2≥p3+p4"] ? 1 : 0,
                " p3≥p45:", feats(cp,a,E,lam)["p3≥p45"] ? 1 : 0,
                " p5≥p3:", feats(cp,a,E,lam)["p5≥p3"] ? 1 : 0)
        length(rows) >= 20 && break
    end
    hi = filter(x->x[2] > 1.19, rows)
    println("\n天花板 > 1.19 的片：", length(hi), " / ", length(rows))
    for (r,c,cp,fl) in hi
        println("   c=", round(c,digits=6), " 实例=", round.(cp,digits=4), " 特征=", fl)
    end
end
main()
