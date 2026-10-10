include("a4_lib.jl")
const A4C = A4(C_TARGET, [:p1, :p45], false, false)
function show(p, label)
    cs = opt_makespan(p, 4); pn = p ./ cs
    ms, asg, load = a4_sim(pn, A4C)
    println(label, "  C*=", round(cs, digits=6), "  makespan=", round(ms, digits=6),
            "  ratio=", round(ms / cs, digits=6))
    println("   p=", round.(pn, digits=4))
    println("   asg=", asg, "  loads=", round.(load, digits=4))
    println("   branch: p1=", round(pn[1], digits=4), " p4+p5=", round(pn[4] + pn[5], digits=4),
            "  Λ=", pn[1] >= pn[4] + pn[5] ? "p1" : "p45")
end
# (1,6) 构造：M1∉E5 且 M1∈E6 argmax
show([0.5, 0.4, 0.4, 0.35, 0.35, 0.3], "(1,6)?")
# (5,10) 临界结构构造：p5 接收机 X 最后被兜底砸中
show([0.61, 0.5, 0.5, 0.4, 0.4, 0.4, 0.3, 0.3, 0.3, 0.3], "(5,10)-critical?")
# 经典临界实例
show([0.6, 0.5, 0.5, 0.4, 0.4, 0.4, 0.3, 0.3, 0.3, 0.3], "classic-critical")
# Λ=p1 分支 M1 被兜底（构造的 (1,10)@full1）
show([0.6, 0.35, 0.3, 0.3, 0.3, 0.28, 0.28, 0.28, 0.28, 0.28], "(1,10)@full1?")
