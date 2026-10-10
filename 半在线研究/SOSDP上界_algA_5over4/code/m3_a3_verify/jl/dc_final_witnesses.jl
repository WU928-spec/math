include("a4_lib.jl")
const A4C = A4(C_TARGET, [:p1, :p45], false, false)
function chk(p, pair, label)
    cs = opt_makespan(p, 4); pn = p ./ cs
    ms, asg, load = a4_sim(pn, A4C)
    i, j = pair
    ok = any(mm -> i in asg[mm] && j in asg[mm], 1:4)
    br = pn[1] >= pn[4] + pn[5] - 1e-12 ? (pn[4] + pn[5] >= pn[1] - 1e-12 ? "both" : "p1") : "p45"
    println(rpad(label, 22), " ($i,$j)同机=$ok  branch=$br  ratio=", round(ms, digits=4),
            "  min=", round(minimum(pn), digits=4), "  asg=", asg)
end
chk([0.7, 0.5, 0.5, 0.5, 0.35, 0.35, 0.35, 0.35, 0.3], (5, 9), "(5,9) X=M2 构造")
chk([0.55, 0.55, 0.55, 0.4, 0.35, 0.3, 0.3, 0.3, 0.28], (5, 9), "(5,9) X=M4 构造")
chk([8 / 15, 8 / 15, 8 / 15, 4 / 15, 4 / 15, 4 / 15], (1, 6), "(1,6) 边界 b1")
chk([1, 1 / 2, 2 / 5, 2 / 5, 7 / 20, 3 / 10], (5, 6), "(5,6) b1 反例")
chk([0.61, 0.52, 0.5, 0.4, 0.4, 0.4, 0.3, 0.3, 0.3, 0.3], (6, 10), "(6,10) Y临界 构造")
