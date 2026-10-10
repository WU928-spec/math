include("a4_lib.jl"); include("a4_milp10.jl")
function run()
    best=-Inf; bestln=""
    for ln in readlines("/tmp/cb_above.txt")
        f=parse.(Int,split(ln,"\t")); mid=div(length(f),2)
        c = piece_ceiling_milp(f[1:mid], f[mid+1:end])
        println("  天花板 = ", round(c, digits=6), "  ", ln)
        c > best && (best=c; bestln=ln)
    end
    println("=== 分支 B 精确上界 = ", round(best, digits=8), "  （片 ", bestln, "）")
end
run()
