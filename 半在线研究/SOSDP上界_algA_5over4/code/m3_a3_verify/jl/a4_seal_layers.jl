# a4_seal_layers.jl —— 层 (1)/(3) 的逐片带隙封底（轨迹约束 MILP）
#   对片清单中「z 兜底（末步 mask=0）且计数形状命中目标层」的片，
#   检查 milp_sel(level=6/5+1e-4) 是否不可行（=该片封底 ≤6/5+1e-4，余量 ≫ 容差，事实严谨）。
#   用法：julia --project=. a4_seal_layers.jl <pieces.txt> <full45|full1> <target counts 如 2,2,2,1> [采样数]
include("a4_lib.jl")
include("a4_milp10.jl")
import Cbc

function load_pieces(file)
    out = Tuple{Vector{Int}, Vector{Int}}[]
    for line in eachline(file)
        isempty(strip(line)) && continue
        v = parse.(Int, split(line))
        n2 = length(v); @assert iseven(n2)
        h = n2 ÷ 2
        push!(out, (v[1:h], v[(h+1):end]))
    end
    return out
end

"放 z 前计数向量（初始 4 台各 1 件 + 步 5..n−1 的接收）"
function pre_z_counts(k)
    c = ones(Int, 4)
    for j in 1:(length(k)-1); c[k[j]] += 1; end
    return sort(c, rev = true)
end

function main()
    file, preds, ctarget = ARGS[1], Symbol(ARGS[2]), ARGS[3]
    nsample = length(ARGS) >= 4 ? parse(Int, ARGS[4]) : 0
    solver = length(ARGS) >= 5 ? ARGS[5] : "highs"
    if solver == "cbc"
        OPTIMIZER[] = Cbc.Optimizer
        println("求解器 = CBC（交叉验证）")
    else
        println("求解器 = HiGHS")
    end
    target = sort(parse.(Int, split(ctarget, ",")), rev = true)
    pieces = load_pieces(file)
    sel = filter(p -> p[2][end] == 0 && pre_z_counts(p[1]) == target, pieces)
    println("片总数 $(length(pieces))；命中目标形状（z 兜底 + 计数 $target）：$(length(sel))")
    isempty(sel) && return
    if nsample > 0 && nsample < length(sel)
        sel = sel[round.(Int, range(1, length(sel), length = nsample))]
        println("采样 $(length(sel)) 条计时…")
    end
    t0 = time(); nreach = 0; ntimeout = 0; worst = -Inf; worstp = nothing
    for (i, (k, masks)) in enumerate(sel)
        v, el, st = milp_sel(k, masks; timelimit = 60.0, preds = preds)   # 精确天花板
        if st != OPTIMAL
            ntimeout += 1
            println("  ?? 状态=$st k=$k masks=$masks")
        else
            v > worst && (worst = v; worstp = (k, masks))
            if v > 6 / 5 - 1e-6
                nreach += 1
                println("  !! 片天花板 ≥ 6/5−1e-6：$(round(v, digits=8))  k=$k masks=$masks")
            end
        end
        if i % 50 == 0
            dt = time() - t0
            println("  …$i/$(length(sel))  已用 $(round(dt, digits=1)) s，均 $(round(dt/i, digits=3)) s/片，当前最大 $(round(worst, digits=6))")
            flush(stdout)
        end
    end
    dt = time() - t0
    println("完成：$(length(sel)) 片，天花板≥6/5−1e-6 的 $(nreach) 条，异常 $(ntimeout)，总 $(round(dt, digits=1)) s，均 $(round(dt/length(sel), digits=3)) s/片")
    println("全层最大天花板 = $(round(worst, digits=8))  @ $(worstp)")
    nsample > 0 && println("外推：$(round(dt/length(sel), digits=3)) s/片")
end

main()
