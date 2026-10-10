# razor 序列 + 随时停止权的 minimax 博弈值（精确整数 DP）
# 对手：固定递减序列（razor 十倍整数），每步放置后可选择停止（比值=当前makespan/前缀OPT）或继续；
# 算法：确定性在线规则（任意放置）。博弈值 = max_对手 min_算法 比值。
# 若值=1.2 ⟹ 任何确定性算法在 razor 某前缀上 ≥6/5 ⟹ 下界 6/5 ⟹ A4c 最优。
const SEQ = [6, 5, 5, 4, 4, 4, 3, 3, 3, 3]   # razor ×10
const M = 4

# 精确 OPT（整数分支定界）
function opt_int(p::Vector{Int})
    load = zeros(Int, M); best = Ref(typemax(Int))
    function dfs(i::Int)
        if i > length(p); best[] = min(best[], maximum(load)); return; end
        for m in 1:M
            load[m] += p[i]
            load[m] < best[] && dfs(i + 1)
            load[m] -= p[i]
        end
    end
    dfs(1); return best[]
end

const OPTS = [opt_int(SEQ[1:j]) for j in 1:length(SEQ)]

# DP：V(j, loads) = 已放 j 件、当前负载 loads（排序去对称）时，对手行动前的博弈值（已乘 10 的整数负载）
# V(j) = max( 停止值 maxload/OPT[j],  继续值 min_m V(j+1, loads+p_{j+1}→m) )
const MEMO = Dict{Tuple{Int,NTuple{4,Int}},Float64}()
const CHOICE = Dict{Tuple{Int,NTuple{4,Int}},Int}()   # 最优放置（供提取逃逸策略）

function V(j::Int, loads::NTuple{4,Int})::Float64
    key = (j, loads)
    haskey(MEMO, key) && return MEMO[key]
    stopval = j == 0 ? 0.0 : maximum(loads) / OPTS[j]
    if j == length(SEQ)
        MEMO[key] = stopval; return stopval
    end
    pnext = SEQ[j + 1]
    contval = Inf; bestm = 0
    for m in 1:M
        nl = collect(loads); nl[m] += pnext; nlt = Tuple(sort(nl))
        v = V(j + 1, nlt)
        if v < contval; contval = v; bestm = m; end
    end
    CHOICE[key] = bestm
    MEMO[key] = max(stopval, contval)
    return MEMO[key]
end

function main()
    v0 = V(0, (0, 0, 0, 0))
    println("razor 序列 + 停止权 博弈值 = ", v0, "  （6/5 = ", 6/5, "）")
    println("状态数 = ", length(MEMO))
    # 提取一条最优对抗线路（算法最优应对下的停止点）
    loads = (0, 0, 0, 0)
    for j in 0:length(SEQ)-1
        stopval = maximum(loads) / OPTS[max(j, 1)]
        j == 0 && (stopval = 0.0)
        m = get(CHOICE, (j, loads), 0)
        println("步 $j 负载=$loads 停止值=$(round(stopval, digits=4)) 算法最优放置→M$m")
        m == 0 && break
        nl = collect(loads); nl[m] += SEQ[j + 1]; loads = Tuple(sort(nl))
    end
    println("末态负载=$loads  停止值=$(maximum(loads)/OPTS[length(SEQ)])")
end
main()
