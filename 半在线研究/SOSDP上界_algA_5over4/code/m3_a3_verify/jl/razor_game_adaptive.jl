# 自适应对手博弈：对手每步从菜单选下一件（递减、≤NMAX 件、可随时停止），算法任意确定性放置。
# 博弈值 = 该菜单下最强对手能逼出的最小比值（对全体确定性算法）。
# 注意：菜单为离散有理值，ρ-对抗族（无理数件）不在菜单内——此博弈给"razor 型前缀陷阱"的强度下界。
const M = 4
const NMAX = 11
const MENU = [6, 5, 4, 3, 2]          # 0.6..0.2（×10）
const START = [6, 5]                  # 对手首件候选

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

# 状态：(loads 排序元组, last 上一件, seq 已放序列)。OPT 依赖序列——存进状态键（序列本身）。
# 为控制状态数，序列即键的一部分（OPT 按需现算带缓存）。
const OPTCACHE = Dict{Vector{Int},Int}()
function optc(seq::Vector{Int})
    get!(OPTCACHE, seq) do; opt_int(seq); end
end

const MEMO = Dict{Tuple{NTuple{4,Int},Int,Vector{Int}},Float64}()

function V(loads::NTuple{4,Int}, last::Int, seq::Vector{Int})::Float64
    stopval = isempty(seq) ? 0.0 : maximum(loads) / optc(seq)
    length(seq) >= NMAX && return stopval
    key = (loads, last, seq)
    haskey(MEMO, key) && return MEMO[key]
    cont = -Inf
    for x in MENU
        last > 0 && x > last && continue          # 递减约束
        # 算法最优放置 x
        best = Inf
        for m in 1:M
            nl = collect(loads); nl[m] += x
            v = V(Tuple(sort(nl)), x, [seq; x])
            v < best && (best = v)
        end
        cont = max(cont, best)
    end
    MEMO[key] = max(stopval, cont)
    return MEMO[key]
end

function main()
    # 对手从 razor 前缀 (6,5,5,4) 之后开始自适应（考察 razor 陷阱的真实强度）
    loads = (6, 5, 5, 4) |> collect |> sort |> Tuple
    v = V(loads, 4, [6, 5, 5, 4])
    println("razor 前缀 (0.6,0.5,0.5,0.4) 之后的自适应博弈值 = ", v)
    println("状态数 = ", length(MEMO), "，OPT 缓存 = ", length(OPTCACHE))
    # 全自由（首件也从菜单）的对照
    empty!(MEMO)
    v2 = V((0, 0, 0, 0), 0, Int[])
    println("全自由菜单博弈值 = ", v2, "（状态数 ", length(MEMO), "）")
end
main()
