# a4_bench_cuts.jl —— 比较「无冲突割」vs「有冲突割」的封底用时（判定必须一致）
#   用法：julia --project=. a4_bench_cuts.jl <片清单> <N> <level>
include("a4_lib.jl")
include("a4_milp10.jl")

function main()
    path = ARGS[1]
    all = [strip(l) for l in readlines(path) if !isempty(strip(l))]
    N = parse(Int, ARGS[2]); level = parse(Float64, ARGS[3])
    rows = all[1:min(N, length(all))]
    tA = 0.0; tB = 0.0; agree = 0
    for (i, ln) in enumerate(rows)
        f = parse.(Int, split(ln, '\t')); mid = div(length(f), 2)
        k = f[1:mid]; masks = f[mid+1:end]
        a = time(); rA = piece_reaches(k, masks, level; cuts = false); dA = time() - a
        a = time(); rB = piece_reaches(k, masks, level; cuts = true); dB = time() - a
        tA += dA; tB += dB
        rA == rB ? (agree += 1) : println("  ✗ 判定不一致: ", ln, "  无割=", rA, " 有割=", rB)
        println("片 ", lpad(i, 3), "  无割 ", lpad(round(dA, digits = 2), 6), " s   有割 ",
                lpad(round(dB, digits = 2), 6), " s   加速 ", round(dA / max(dB, 1e-9), digits = 2), "×")
        flush(stdout)
    end
    println("\n汇总：无割 ", round(tA, digits = 1), " s；有割 ", round(tB, digits = 1),
            " s；加速 ", round(tA / max(tB, 1e-9), digits = 2), "×；判定一致 ", agree, "/", length(rows))
end
main()
