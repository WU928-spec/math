# a4_l3_recvceil.jl —— 层 (3) 逐片"接收机目标"天花板（min+z 口径，供手证案例树覆盖性核对）
#   封底用的是 makespan（max_m ℓ_m），填充主导的片压到 ρ=1.1805，razor 族（7/6）看不见。
#   这里每片只优化 z 接收机的终载 ℓ[k[end]]（无选机二元，比 milp_sel 便宜），
#   输出：天花板分布 + 接近 7/6 的紧片清单（手证案例树必须覆盖的那些）。
include("a4_lib.jl")
include("a4_milp10.jl")

function load_pieces(file)
    out = Tuple{Vector{Int}, Vector{Int}}[]
    for line in eachline(file)
        isempty(strip(line)) && continue
        v = parse.(Int, split(line)); h = length(v) ÷ 2
        push!(out, (v[1:h], v[(h+1):end]))
    end
    return out
end

function pre_z_counts(k)
    c = ones(Int, 4)
    for j in 1:(length(k)-1); c[k[j]] += 1; end
    return sort(c, rev = true)
end

"单片：max z 接收机终载（preds 分支），返回 (sup, 最优 p)"
function recv_ceiling(k, masks; preds)
    n = 4 + length(k)
    m, P = _base(n; preds = preds)
    set_silent(m); set_time_limit_sec(m, 60.0)
    ℓ = _trace!(m, P, k, masks; n = n, preds = preds)
    recv = k[end]
    @objective(m, Max, ℓ[recv])
    optimize!(m)
    termination_status(m) == OPTIMAL || return NaN, Float64[]
    return objective_value(m), value.(P)
end

function run(file, preds, out)
    pieces = load_pieces(file)
    sel = filter(p -> p[2][end] == 0 && pre_z_counts(p[1]) == [2, 2, 2, 2], pieces)
    println("$(file)：命中 $(length(sel)) 片")
    io = open(out, "w")
    println(io, "# sup\t k \t masks \t p*")
    worst = -Inf; ntight = 0; t0 = time()
    for (i, (k, masks)) in enumerate(sel)
        v, pv = recv_ceiling(k, masks; preds = preds)
        isnan(v) && (println("  ?? 不可行/超时 k=$k"); continue)
        v > worst && (worst = v)
        tight = v > 7 / 6 - 0.02
        tight && (ntight += 1)
        println(io, join((round(v, digits = 6), join(k, ","), join(masks, ","),
                          join(round.(pv, digits = 4), ",")), "\t"))
        if i % 200 == 0
            println("  …$i/$(length(sel))  用 $(round(time()-t0, digits=0)) s，当前最大 $(round(worst, digits=6))，紧片 $ntight")
            flush(stdout); flush(io)
        end
    end
    close(io)
    println("完成 $(file)：最大 = $(round(worst, digits=8))，紧片（>7/6−0.02）= $(ntight)，总用时 $(round(time()-t0, digits=1)) s")
end

run(ARGS[1], Symbol(ARGS[2]), ARGS[3])
