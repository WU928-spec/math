include("a4_lib.jl")
p = [0.5833,0.5833,0.5,0.5,0.4167,0.3333,0.3333,0.3333,0.3333]
println("opt_makespan(p,4) = ", opt_makespan(p,4))
# 暴力复核：枚举所有装箱
function brute(p, m)
    n = length(p); best = Inf
    asg = zeros(Int, n)
    function rec(i)
        i > n && (best = min(best, maximum([sum(p[asg.==b]) for b in 1:m])); return)
        for b in 1:m; asg[i]=b; rec(i+1); end
    end
    rec(1); best
end
println("暴力 = ", brute(p,4))
# 还有 ratio 的双归一化 bug
pn = p ./ opt_makespan(p,4)
a4 = A4(C_TARGET, [:p1,:p45], false, false)
println("a4_sim(pn)[1] = ", a4_sim(pn, a4)[1], "  真正比值 = ", a4_sim(pn, a4)[1]/opt_makespan(pn,4))
