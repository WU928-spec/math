# a4_bench.jl —— 封底算法的加速对比基准
#   对同一批片，比 V0（现状：4 次可行性 MILP）与 V1（单次求解 + 最重机二元 z）的
#   用时与判定是否一致。用法：
#     julia --project=. a4_bench.jl <片清单> <N> <level>
include("a4_lib.jl")
include("a4_milp10.jl")

function main()
    path = ARGS[1]; N = parse(Int, ARGS[2]); level = parse(Float64, ARGS[3])
    rows = [strip(l) for l in readlines(path) if !isempty(strip(l))][1:min(N, count(!isempty, readlines(path)))]
    t0 = 0.0; t1 = 0.0; agree = 0; v0tab = Bool[]; v1tab = Bool[]
    for (i, ln) in enumerate(rows)
        f = parse.(Int, split(ln, '\t')); mid = div(length(f), 2)
        k = f[1:mid]; masks = f[mid+1:end]
        a = time(); r0 = piece_reaches(k, masks, level); d0 = time() - a
        a = time(); _, el1, st1 = milp_sel(k, masks; level = level); r1 = (st1 == OPTIMAL); d1 = time() - a
        t0 += d0; t1 += d1
        r0 == r1 ? (agree += 1) : println("  ✗ 判定不一致: ", ln, "  V0=", r0, " V1=", r1)
        push!(v0tab, r0); push!(v1tab, r1)
        println("片 ", lpad(i, 3), "  V0(4次) ", round(d0, digits = 2), " s   V1(1次) ", round(d1, digits = 2),
                " s  判定 ", r0, "/", r1, "  加速 ", round(d0 / max(d1, 1e-9), digits = 2), "×")
        flush(stdout)
    end
    println("\n汇总：V0 合计 ", round(t0, digits = 1), " s；V1 合计 ", round(t1, digits = 1), " s；总加速 ",
            round(t0 / max(t1, 1e-9), digits = 2), "×；判定一致 ", agree, "/", length(rows))
    println("达到 level 的片：V0 ", count(v0tab), " 条，V1 ", count(v1tab), " 条")
end
main()
