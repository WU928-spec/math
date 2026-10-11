# 下界博弈机 v2（2026-10-11）：精确整数算术；任意 M；固定序列（含停止权）+ 自适应菜单两种模式
# 校准：m=3 SSW → c；m=4 九任务 (1³,r³,s³) → ρ=c。主攻：自适应细菜单能否 >ρ。
using Printf

const SCALE = 10^6
intval(x) = round(Int64, x * SCALE)

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

# 固定序列博弈值（逐前缀停止权）。状态 (j, 负载排序元组)
function game_fixed(seq::Vector{Int64}, M::Int)
    n = length(seq)
    OPTS = [opt_int(copy(seq[1:j]), M) for j in 1:n]
    memo = Dict{Any,Float64}()
    z0 = ntuple(_ -> Int64(0), M)
    function V(j::Int, loads)::Float64
        key = (j, loads)
        haskey(memo, key) && return memo[key]
        stopval = j == 0 ? 0.0 : maximum(loads) / OPTS[j]
        if j == n; memo[key] = stopval; return stopval; end
        cont = Inf
        for m in 1:M
            nl = collect(loads); nl[m] += seq[j+1]
            v = V(j + 1, Tuple(sort(nl)))
            v < cont && (cont = v)
        end
        memo[key] = max(stopval, cont)
        return memo[key]
    end
    V(0, z0)
end

# 自适应菜单博弈值。状态 = (负载排序元组, 各菜单件计数元组)；对手选下一件（≤上一件），可随时停
function game_adaptive(menu::Vector{Int64}, M::Int, NMAX::Int)
    K = length(menu)
    issorted(menu; rev = true) || error("menu 需降序")
    OPTCACHE = Dict{Any,Int64}()
    function optc(cnt)
        get!(OPTCACHE, cnt) do
            pcs = Int64[]
            for i in 1:K; for _ in 1:cnt[i]; push!(pcs, menu[i]); end; end
            opt_int(pcs, M)
        end
    end
    memo = Dict{Any,Float64}()
    zc = ntuple(_ -> 0, K)
    zl = ntuple(_ -> Int64(0), M)
    function V(loads, cnt)::Float64
        key = (loads, cnt)
        haskey(memo, key) && return memo[key]
        total = sum(cnt)
        stopval = total == 0 ? 0.0 : maximum(loads) / optc(cnt)
        total >= NMAX && (memo[key] = stopval; return stopval)
        last = total == 0 ? menu[1] + 1 : menu[findlast(>(0), collect(cnt))]
        cont = -Inf
        for i in 1:K
            menu[i] > last && continue
            best = Inf
            for m in 1:M
                nl = collect(loads); nl[m] += menu[i]
                nc = collect(cnt); nc[i] += 1
                v = V(Tuple(sort(nl)), Tuple(nc))
                v < best && (best = v)
            end
            best > cont && (cont = best)
        end
        memo[key] = max(stopval, cont)
        return memo[key]
    end
    V(zl, zc), length(memo)
end

function main()
    ρ = (1 + sqrt(37)) / 6
    @printf("目标常数 ρ = c = %.10f\n", ρ)
    # 校准 1：m=3 SSW（x², (1−x)², (1/3)³），x=(13−√37)/12
    x = (13 - sqrt(37)) / 12
    v3 = game_fixed(intval.([x, x, 1 - x, 1 - x, 1/3, 1/3, 1/3]), 3)
    @printf("[校准] m=3 SSW：%.10f（应=ρ，差 %.1e）\n", v3, v3 - ρ)
    # 校准 2：m=4 九任务 (1³, r³, s³)
    r = (2 + sqrt(37)) / 11; s = (13 + sqrt(37)) / 33
    v9 = game_fixed(intval.([1, 1, 1, r, r, r, s, s, s]), 4)
    @printf("[校准] m=4 九任务：%.10f（应=ρ，差 %.1e）\n", v9, v9 - ρ)

    # 主攻：自适应细菜单（ρ 族值 + razor 值 + 1/3 + 细粒）
    menu = intval.([1.0, r, 0.6, s, 0.5, 0.4, 1/3, 0.3, 0.25])
    for NMAX in (10, 12)
        v, ns = game_adaptive(menu, 4, NMAX)
        @printf("[自适应] 9值菜单 NMAX=%d：博弈值 = %.6f（%s ρ）  状态数=%d\n",
                NMAX, v, v > ρ + 1e-6 ? "超过" : "≤", ns)
    end
end
main()
