# 前缀陷阱博弈值（2026-10-11）：前缀 (0.6,0.5,0.5,0.4,0.4) 后按算法步 5 落点分三叉：
#   吸收(p5→M1)：对手停 → 1.0/OPT(前缀) = 1.25（无需 DP）
#   fullest(p5→M2→0.9)：状态 (0.4,0.5,0.6,0.9)，对手自选尾巴
#   spread(p5→M4→0.8)：状态 (0.5,0.5,0.6,0.8)，对手自选尾巴
# 尾巴：自适应菜单 {0.4, 1/3, 0.3, 0.25}（≤0.4 递减），总长 ≤11，含停止权
# 陷阱值 = min(1.25, B, C)；若 >ρ 则为新下界
using Printf
const SCALE = 10^6
i10(x) = round(Int64, x * SCALE)

function opt_int(pieces::Vector{Int64}, M::Int)
    sort!(pieces; rev = true)
    load = zeros(Int64, M); best = Ref{Int64}(typemax(Int64))
    function dfs(i::Int)
        if i > length(pieces); best[] = min(best[], maximum(load)); return; end
        for m in 1:M
            (m > 1 && load[m] == load[m-1]) && continue
            load[m] += pieces[i]
            load[m] < best[] && dfs(i + 1)
            load[m] -= pieces[i]
        end
    end
    dfs(1); return best[]
end

const PREFIX = i10.([0.6, 0.5, 0.5, 0.4, 0.4])
const TAILMENU = i10.([0.4, 1/3, 0.3, 0.25])
const TAILCAP = 6          # 尾巴最多 6 件（总 11）
const OPT5 = opt_int(copy(PREFIX), 4)

# 分支子博弈：从负载态 loads（排序）、尾巴计数 cnt、上一尾部件 last 出发
function branch_value(loads0::NTuple{4,Int64})
    OPTCACHE = Dict{Any,Int64}()
    function optc(cnt)
        get!(OPTCACHE, cnt) do
            pcs = copy(PREFIX)
            for i in 1:4; for _ in 1:cnt[i]; push!(pcs, TAILMENU[i]); end; end
            opt_int(pcs, 4)
        end
    end
    memo = Dict{Any,Float64}()
    function V(loads, cnt, last)::Float64
        key = (loads, cnt, last)
        haskey(memo, key) && return memo[key]
        total = sum(cnt)
        stopval = maximum(loads) / optc(cnt)
        total >= TAILCAP && (memo[key] = stopval; return stopval)
        cont = -Inf
        for i in 1:4
            TAILMENU[i] > last && continue
            best = Inf
            for m in 1:4
                nl = collect(loads); nl[m] += TAILMENU[i]
                nc = collect(cnt); nc[i] += 1
                v = V(Tuple(sort(nl)), Tuple(nc), TAILMENU[i])
                v < best && (best = v)
            end
            best > cont && (cont = best)
        end
        memo[key] = max(stopval, cont)
        return memo[key]
    end
    V(loads0, (0, 0, 0, 0), TAILMENU[1]), length(memo)
end

function main()
    ρ = (1 + sqrt(37)) / 6
    @printf("前缀 OPT = %.4f（吸收支停比值 = %.4f）\n", OPT5 / SCALE, 1.0 / (OPT5 / SCALE))
    # 步 5 三分叉后的负载态（排序）
    abs_state = Tuple(sort(i10.([0.6 + 0.4, 0.5, 0.5, 0.4])))   # 吸收（p5→M1）
    ful_state = Tuple(sort(i10.([0.6, 0.5 + 0.4, 0.5, 0.4])))   # fullest（p5→M2）
    spr_state = Tuple(sort(i10.([0.6, 0.5, 0.5, 0.4 + 0.4])))   # spread（p5→M4）
    vA = 1.0 / (OPT5 / SCALE)                                   # 吸收支：立即停止
    @printf("分支 A（吸收）：对手立即停 ⟹ %.6f\n", vA)
    vB, nB = branch_value(ful_state)
    @printf("分支 B（fullest）：尾巴子博弈值 = %.6f（%s ρ）  状态=%d\n", vB, vB > ρ ? "超" : "≤", nB); flush(stdout)
    vC, nC = branch_value(spr_state)
    @printf("分支 C（spread）：尾巴子博弈值 = %.6f（%s ρ）  状态=%d\n", vC, vC > ρ ? "超" : "≤", nC); flush(stdout)
    trap = min(vA, vB, vC)
    @printf("** 前缀陷阱值 = min(A,B,C) = %.6f（对照 ρ=%.6f、6/5=%.6f）\n", trap, ρ, 1.2)
    if trap > ρ + 1e-6
        println("*** 新下界候选成立：任何确定性算法在 razor 前缀的某条延续上 ≥ ", trap, " ***")
    end
end
main()
