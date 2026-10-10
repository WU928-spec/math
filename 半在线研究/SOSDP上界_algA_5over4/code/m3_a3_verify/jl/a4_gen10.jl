# a4_gen10.jl —— n=10 的**全域**（不加卡点谓词）轨迹枚举：两个 Λ 分支各跑一次
#   用法：julia --project=. a4_gen10.jl <full1|full45> <budget> [shard_i] [shard_k]
#   产出：fam10_gen_<mode>_<i>.txt
include("a4_lib.jl")
include("a4_milp10.jl")

const NTT = 10

function dfsgen(mode::Symbol, budget::Int, si::Int, sk::Int)
    leaves = Dict{String,Vector{Any}}(); nodes = Ref(0); nprune = Ref(0); hit = Ref(false)
    opts = Vector{Tuple{Vector{Int},Int}}()
    for mask in 0:15
        Ej = [m for m in 1:4 if (mask >> (m - 1)) & 1 == 1]
        for aj in (isempty(Ej) ? (1:4) : Ej); push!(opts, (Ej, aj)); end
    end
    function rec(j::Int, steps::Vector{Any})
        nodes[] += 1
        nodes[] % 200 == 0 && (println("  [进度] 节点 ", nodes[], "  剪枝 ", nprune[], "  叶子 ", length(leaves)); flush(stdout))
        nodes[] > budget && (hit[] = true; return)
        if j > NTT
            leaves[string(join([(s[2], join(sort(s[1]), "")) for s in steps], "/"))] = copy(steps)
            return
        end
        kp = Int[s[2]::Int for s in steps]
        mp = [sum(1 << (m - 1) for m in (s[1]::Vector{Int}); init = 0) for s in steps]
        for (idx, (Ej, aj)) in enumerate(opts)
            (j != 5 || ((idx - 1) % sk == si)) || continue
            piece_feasible(vcat(kp, aj), vcat(mp, sum(1 << (m - 1) for m in Ej; init = 0));
                           preds = mode) || (nprune[] += 1; continue)
            rec(j + 1, vcat(steps, Any[(Ej, aj)]))
            hit[] && return
        end
    end
    rec(5, Any[])
    println("DFS-GEN(", mode, ") 节点 ", nodes[], "  剪枝 ", nprune[], "  叶子 ", length(leaves),
            hit[] ? "  [预算用尽]" : "  [完全]")
    open("fam10_gen_$(mode)_$(si).txt", "w") do io
        for (_, steps) in leaves
            ks = Int[s[2]::Int for s in steps]
            ms = [sum(1 << (m - 1) for m in s[1]::Vector{Int}; init = 0) for s in steps]
            println(io, join(vcat(ks, ms), "\t"))
        end
    end
end

function main()
    mode = Symbol(ARGS[1]); budget = parse(Int, ARGS[2])
    si = length(ARGS) >= 4 ? parse(Int, ARGS[3]) : 0
    sk = length(ARGS) >= 4 ? parse(Int, ARGS[4]) : 1
    dfsgen(mode, budget, si, sk)
end
main()
