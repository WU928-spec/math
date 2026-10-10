# a4_genN.jl —— 任意 n 的轨迹枚举（MILP 预言机），用于"测真实规模"
#   用法：julia --project=. a4_genN.jl <full1|full45> <n> <budget>
include("a4_lib.jl")
include("a4_milp10.jl")

function dfsgen(mode::Symbol, n::Int, budget::Int)
    leaves = Ref(0); nodes = Ref(0); nprune = Ref(0); hit = Ref(false)
    opts = Vector{Tuple{Vector{Int},Int}}()
    for mask in 0:15
        Ej = [m for m in 1:4 if (mask >> (m - 1)) & 1 == 1]
        for aj in (isempty(Ej) ? (1:4) : Ej); push!(opts, (Ej, aj)); end
    end
    function rec(j::Int, steps::Vector{Any})
        nodes[] += 1
        nodes[] > budget && (hit[] = true; return)
        if j > n
            leaves[] += 1; return
        end
        kp = Int[s[2]::Int for s in steps]
        mp = [sum(1 << (m - 1) for m in (s[1]::Vector{Int}); init = 0) for s in steps]
        for (Ej, aj) in opts
            piece_feasible(vcat(kp, aj), vcat(mp, sum(1 << (m - 1) for m in Ej; init = 0));
                           preds = mode) || (nprune[] += 1; continue)
            rec(j + 1, vcat(steps, Any[(Ej, aj)]))
            hit[] && return
        end
    end
    rec(5, Any[])
    println(mode, "  n=", n, "  节点 ", nodes[], "  剪枝 ", nprune[], "  片(叶子) ", leaves[],
            hit[] ? "  [预算用尽: > " * string(div(leaves[], 1)) * " 片]" : "  [完全]")
    return leaves[]
end

function main()
    mode = Symbol(ARGS[1]); n = parse(Int, ARGS[2]); budget = parse(Int, ARGS[3])
    dfsgen(mode, n, budget)
end
main()
