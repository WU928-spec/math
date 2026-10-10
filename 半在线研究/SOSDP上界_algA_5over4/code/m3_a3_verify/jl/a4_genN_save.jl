# a4_genN_save.jl —— 任意 n 的轨迹枚举并存档（供逐片封底用）
#   用法：julia --project=. a4_genN_save.jl <full1|full45> <n> <outfile>
#   输出格式（与 fam10_leaves2_all.txt 一致）：k5..kn \t mask5..maskn
include("a4_lib.jl")
include("a4_milp10.jl")

function dfsgen(mode::Symbol, n::Int, io)
    leaves = 0; nprune = 0
    opts = Vector{Tuple{Vector{Int},Int}}()
    for mask in 0:15
        Ej = [m for m in 1:4 if (mask >> (m - 1)) & 1 == 1]
        for aj in (isempty(Ej) ? (1:4) : Ej); push!(opts, (Ej, aj)); end
    end
    function rec(j::Int, steps::Vector{Any})
        if j > n
            leaves += 1
            kp = [s[2]::Int for s in steps]
            mp = [sum(1 << (m - 1) for m in (s[1]::Vector{Int}); init = 0) for s in steps]
            println(io, join(kp, "\t") * "\t" * join(mp, "\t"))
            return
        end
        kp = Int[s[2]::Int for s in steps]
        mp = [sum(1 << (m - 1) for m in (s[1]::Vector{Int}); init = 0) for s in steps]
        for (Ej, aj) in opts
            piece_feasible(vcat(kp, aj), vcat(mp, sum(1 << (m - 1) for m in Ej; init = 0));
                           preds = mode) || (nprune += 1; continue)
            rec(j + 1, vcat(steps, Any[(Ej, aj)]))
        end
    end
    rec(5, Any[])
    return leaves, nprune
end

function main()
    mode = Symbol(ARGS[1]); n = parse(Int, ARGS[2]); out = ARGS[3]
    t0 = time()
    leaves, nprune = open(out, "w") do io
        dfsgen(mode, n, io)
    end
    println(mode, "  n=", n, "  片 ", leaves, "  剪枝 ", nprune, "  用时 ", round(time() - t0, digits = 1), " s [完全]")
end
main()
