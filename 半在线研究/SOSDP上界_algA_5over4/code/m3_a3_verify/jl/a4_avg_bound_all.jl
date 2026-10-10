# a4_avg_bound_all.jl —— 把「兜底步统一界」在所有 (n, Λ 分支) 上跑一遍
include("a4_lib.jl")
include("a4_avg_bound.jl")

function main()
    println("配置                     统一界")
    for (preds, n) in [(:full1, 9)]
        b = run(preds, true, n, 300.0)
        println("  ⇒ ", preds, "  n=", n, "  →  ", round(b, digits = 6), "\n"); flush(stdout)
    end
end
main()
