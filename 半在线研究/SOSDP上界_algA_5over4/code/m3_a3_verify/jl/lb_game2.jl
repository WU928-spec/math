# 自适应对手主实验（2026-10-11）：菜单含 ρ 族值 + razor 值 + 细粒；问：博弈值能否 > ρ
# 输出即时 flush 到 stdout（后台重定向到日志文件）
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

function game_adaptive(menu::Vector{Int64}, M::Int, NMAX::Int)
    K = length(menu)
    OPTCACHE = Dict{Any,Int64}()
    function optc(cnt)
        get!(OPTCACHE, cnt) do
            pcs = Int64[]
            for i in 1:K; for _ in 1:cnt[i]; push!(pcs, menu[i]); end; end
            opt_int(pcs, M)
        end
    end
    memo = Dict{Any,Float64}()
    zc = ntuple(_ -> 0, K); zl = ntuple(_ -> Int64(0), M)
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
    r = (2 + sqrt(37)) / 11; s = (13 + sqrt(37)) / 33
    menu = intval.([1.0, r, s, 0.5, 0.4, 1/3])
    println("菜单（×$SCALE）：", menu); flush(stdout)
    for NMAX in (9, 11, 12, 14)
        t = time()
        v, ns = game_adaptive(menu, 4, NMAX)
        @printf("[自适应] 8值菜单 NMAX=%2d：博弈值 = %.8f（%s ρ=%.8f，差 %+.2e）  状态=%d  耗时=%.1fs\n",
                NMAX, v, v > ρ + 2e-6 ? "**超过**" : "≤", ρ, v - ρ, ns, time() - t)
        flush(stdout)
    end
end
main()
