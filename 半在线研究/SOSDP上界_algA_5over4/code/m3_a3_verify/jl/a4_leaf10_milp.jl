# a4_leaf10_milp.jl —— 对 fam10_leaves2.txt（经 MILP 预言机枚举出的真片）逐片求天花板
#   用法：julia --project=. a4_leaf10_milp.jl <shard_i> <shard_k> [maxlines]
#   分片规则：行号 % k == i
include("a4_lib.jl")
include("a4_milp10.jl")

function main()
    si = parse(Int, ARGS[1]); sk = parse(Int, ARGS[2])
    maxlines = length(ARGS) >= 3 ? parse(Int, ARGS[3]) : typemax(Int)
    lines = readlines(get(ENV, "FAM10_LEAVES", "fam10_leaves2.txt"))
    nproc = 0; best = -Inf; bestline = 0; nan = 0; hist = Dict{Int,Int}()
    for (idx, ln) in enumerate(lines)
        idx > maxlines && break
        (idx - 1) % sk == si || continue
        f = parse.(Int, split(ln, '\t'))
        mid = div(length(f), 2)
        k = f[1:mid]; masks = f[mid+1:end]
        c = piece_ceiling_milp(k, masks)
        nproc += 1
        if isnan(c)
            nan += 1; println(join([idx, "NaN", join(k, "-"), join(masks, "-")], "\t"))
        else
            println(join([idx, round(c, digits = 8), join(k, "-"), join(masks, "-")], "\t")); flush(stdout)
            c > best && (best = c; bestline = idx)
        end
    end
    println("--- shard ", si, "/", sk, "：处理 ", nproc, " 条，空片 ", nan,
            "，最大天花板 ", round(best, digits = 8), "（第 ", bestline, " 行）")
end
main()
