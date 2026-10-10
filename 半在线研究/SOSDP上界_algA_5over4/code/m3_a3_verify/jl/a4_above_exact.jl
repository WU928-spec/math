# a4_above_exact.jl —— 对"达到 1.2"的片求**精确**天花板（4 次最优化 MILP，慢但准确）
#   用法：julia --project=. a4_above_exact.jl <片清单> [preds: card|full45|full1]
include("a4_lib.jl")
include("a4_milp10.jl")

function main()
    path = ARGS[1]
    preds = length(ARGS) >= 2 ? Symbol(ARGS[2]) : :card
    best = -Inf; bestline = ""
    for (idx, ln) in enumerate(readlines(path))
        ln = strip(ln); isempty(ln) && continue
        f = parse.(Int, split(ln, '\t')); mid = div(length(f), 2)
        k = f[1:mid]; masks = f[mid+1:end]
        c = piece_ceiling_milp(k, masks; preds = preds)
        println("第 ", idx, " 条  片=", join(k, "-"), " | ", join(masks, "-"), "  天花板=", round(c, digits = 8))
        flush(stdout)
        c > best && (best = c; bestline = ln)
    end
    println("=== 最大精确天花板 = ", round(best, digits = 8), "（", bestline, "）")
end
main()
