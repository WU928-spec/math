# 策略蒸馏：提取 razor 陷阱 B 支（fullest 步 5 后）的 DP 最优续投
# 打印：对手最优出牌序列 + 算法每步最优放置 + 各步停止值（对手何时最想停）
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
const TAILCAP = 6

const OPTCACHE = Dict{Any,Int64}()
function optc(cnt)
    get!(OPTCACHE, cnt) do
        pcs = copy(PREFIX)
        for i in 1:4; for _ in 1:cnt[i]; push!(pcs, TAILMENU[i]); end; end
        opt_int(pcs, 4)
    end
end

const MEMOV = Dict{Any,Float64}()
function V(loads, cnt, last)::Float64
    key = (loads, cnt, last)
    haskey(MEMOV, key) && return MEMOV[key]
    total = sum(cnt)
    stopval = maximum(loads) / optc(cnt)
    total >= TAILCAP && (MEMOV[key] = stopval; return stopval)
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
    MEMOV[key] = max(stopval, cont)
    return MEMOV[key]
end

function main()
    ρ = (1 + sqrt(37)) / 6
    # B 支起点（fullest 步 5：p5→M2，0.5→0.9）
    loads = Tuple(sort(i10.([0.6, 0.5 + 0.4, 0.5, 0.4])))
    cnt = (0, 0, 0, 0); last = TAILMENU[1]
    @printf("B 支起点负载（排序）=%s  子博弈值=%.6f\n", string(loads ./ SCALE), V(loads, cnt, last))
    println("—— 最优对局线（对手出牌 → 算法放置 → 负载 | 对手停止值）——")
    while sum(cnt) < TAILCAP
        # 对手选 argmax_i [ min_m V(...) ]
        besti, bestv = 0, -Inf
        for i in 1:4
            TAILMENU[i] > last && continue
            best = Inf
            for m in 1:4
                nl = collect(loads); nl[m] += TAILMENU[i]
                nc = collect(cnt); nc[i] += 1
                v = V(Tuple(sort(nl)), Tuple(nc), TAILMENU[i])
                v < best && (best = v)
            end
            best > bestv && (bestv = best; besti = i)
        end
        besti == 0 && break
        # 若对手此刻停更优，则停
        stopnow = maximum(loads) / optc(cnt)
        # 算法应对 besti：argmin_m
        bestm, bestmv = 0, Inf
        for m in 1:4
            nl = collect(loads); nl[m] += TAILMENU[besti]
            nc = collect(cnt); nc[besti] += 1
            v = V(Tuple(sort(nl)), Tuple(nc), TAILMENU[besti])
            v < bestmv && (bestmv = v; bestm = m)
        end
        nl = collect(loads); nl[bestm] += TAILMENU[besti]
        nc = collect(cnt); nc[besti] += 1
        loads = Tuple(sort(nl)); cnt = Tuple(nc); last = TAILMENU[besti]
        @printf("对手出 %.4f → 算法放 M%d ⟹ 负载 %s | 对手停值 %.4f / 续投值 %.4f\n",
                TAILMENU[besti] / SCALE, bestm, string(collect(loads) ./ SCALE), stopnow, bestmv)
        stopnow >= bestmv - 1e-12 && (println("（对手此时停止更优）"); break)
    end
    @printf("终态负载 %s，makespan/OPT = %.6f（ρ=%.6f）\n",
            string(collect(loads) ./ SCALE), maximum(loads) / optc(cnt), ρ)
end
main()
