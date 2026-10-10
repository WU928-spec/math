# a4_leaf10_level.jl —— 对枚举出的真片逐条检验"天花板是否 > 阈值"（默认 1.2）
#   可行性 MILP 比最优化快得多：4 个"最重机"情形全不可行 ⟹ 该片天花板 ≤ 阈值
#   用法：julia --project=. a4_leaf10_level.jl <shard_i> <shard_k> [level] [maxlines]
#        环境变量 FAM10_LEAVES 指定片清单（默认 fam10_leaves2.txt）
include("a4_lib.jl")
include("a4_milp10.jl")

function main()
    si = parse(Int, ARGS[1]); sk = parse(Int, ARGS[2])
    level = length(ARGS) >= 3 ? parse(Float64, ARGS[3]) : 1.2
    maxlines = length(ARGS) >= 4 ? parse(Int, ARGS[4]) : typemax(Int)
    lines = readlines(get(ENV, "FAM10_LEAVES", "fam10_leaves2.txt"))
    nproc = 0; nabove = 0; above = String[]
    for (idx, ln) in enumerate(lines)
        idx > maxlines && break
        (idx - 1) % sk == si || continue
        f = parse.(Int, split(ln, '\t'))
        mid = div(length(f), 2)
        k = f[1:mid]; masks = f[mid+1:end]
        nproc += 1
        if piece_reaches(k, masks, level)
            nabove += 1; push!(above, ln)
            println(join([idx, "ABOVE", join(k, "-"), join(masks, "-")], "\t")); flush(stdout)
        end
        nproc % 100 == 0 && (println("  [进度] shard ", si, " 已检验 ", nproc); flush(stdout))
    end
    println("--- shard ", si, "/", sk, "（阈值 ", level, "）：检验 ", nproc, " 条，超过阈值 ", nabove, " 条")
    isempty(above) || println("    超标片清单：\n", join(above, "\n"))
end
main()
