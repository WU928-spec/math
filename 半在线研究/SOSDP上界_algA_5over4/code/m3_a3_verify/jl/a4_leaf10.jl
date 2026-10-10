# a4_leaf10.jl —— 对 fam10 家族的各条"片"（轨迹）求精确天花板
#
#   输入 fam10_leaves.txt（12 列：a5..a10、E5..E10 位掩码）
#   对每条片：在 9100 个最优装箱结构上求 max ℓ_max，取最大值 = 该片天花板
#   用法：julia --project=. a4_leaf10.jl <shard_i> <shard_k> [maxlines]
#   （按行号 % k == i 分片，方便多进程并行）
include("common.jl")
using JuMP, HiGHS

const RHO = C_TARGET
const ALP = 4.0 / 15.0
const PACK = partitions(10, 3, 4)         # n=10、每箱 ≤3 件、≤4 箱

"给定一条片（steps = [(Ej,aj), ...] 对应 j=5..10），求天花板；不可行返回 NaN"
function piece_ceiling(steps::Vector{Tuple{Vector{Int},Int}})
    best = -Inf; bp = Float64[]; anyfeas = false
    for blocks in PACK
        m = Model(HiGHS.Optimizer); set_silent(m)
        @variable(m, P[1:10]); for i in 1:10; set_lower_bound(P[i], ALP); end
        for i in 1:9; @constraint(m, P[i] >= P[i+1]); end
        for blk in blocks; @constraint(m, sum(P[i] for i in blk) <= 1.0); end
        @constraint(m, P[4] + P[5] >= P[1])          # Λ = p45 分支
        @constraint(m, P[2] <= P[3] + P[4])          # 家族谓词
        @constraint(m, P[3] <= P[4] + P[5])
        @constraint(m, P[5] <= P[3])
        τ = RHO * (P[4] + P[5])
        ℓ = [AffExpr(0.0) for _ in 1:4]
        for mm in 1:4; ℓ[mm] += P[mm]; end
        for (k, (Ej, aj)) in enumerate(steps)
            j = 4 + k
            pre = copy(ℓ)
            for mm in 1:4
                mm in Ej ? @constraint(m, pre[mm] + P[j] <= τ) : @constraint(m, pre[mm] + P[j] >= τ)
            end
            if isempty(Ej)
                for mm in 1:4; @constraint(m, pre[aj] <= pre[mm]); end
            else
                for mm in Ej; @constraint(m, pre[aj] >= pre[mm]); end
            end
            ℓ[aj] += P[j]
        end
        @variable(m, t)
        for mm in 1:4; @constraint(m, t <= ℓ[mm]); end
        @objective(m, Max, t); optimize!(m)
        if termination_status(m) == OPTIMAL
            anyfeas = true
            if objective_value(m) > best + 1e-12
                best = objective_value(m); bp = value.(P)
            end
        end
    end
    return anyfeas ? (best, bp) : (NaN, Float64[])
end

function main()
    si = parse(Int, ARGS[1]); sk = parse(Int, ARGS[2])
    maxlines = length(ARGS) >= 3 ? parse(Int, ARGS[3]) : typemax(Int)
    lines = readlines(get(ENV, "FAM10_LEAVES", "fam10_leaves.txt"))
    nproc = 0; best = -Inf; bestline = 0; bestp = Float64[]; nan = 0
    for (idx, ln) in enumerate(lines)
        idx > maxlines && break
        (idx - 1) % sk == si || continue
        f = parse.(Int, split(ln, '\t'))
        ks = f[1:6]; ms = f[7:12]
        steps = Tuple{Vector{Int},Int}[]
        for k in 1:6
            Ej = [mm for mm in 1:4 if (ms[k] >> (mm - 1)) & 1 == 1]
            push!(steps, (Ej, ks[k]))
        end
        c, cp = piece_ceiling(steps)
        nproc += 1
        if isnan(c); nan += 1; println(join([idx, "NaN"], "\t"))
        else
            println(join([idx, round(c, digits = 8), round(minimum(cp), digits = 4)], "\t")); flush(stdout)
            if c > best; best = c; bestline = idx; bestp = copy(cp); end
        end
    end
    println("--- shard ", si, "/", sk, "：处理 ", nproc, " 条，不可行(空片) ", nan,
            "，最大天花板 ", round(best, digits = 8), "（第 ", bestline, " 行）")
    best > -Inf && println("    见证 p = ", round.(bestp, digits = 4))
end
main()
