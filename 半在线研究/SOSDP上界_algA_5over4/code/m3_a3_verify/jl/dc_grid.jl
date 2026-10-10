# dc_grid.jl —— 串行跑全部 (branch, n) 的同机判定（单核；先加载采样见证跳过）
include("dc_coloc.jl")

function load_prewits(path::String)
    out = Dict{Tuple{Symbol,Int},Set{Int}}()
    isfile(path) || return out
    for ln in eachline(path)
        f = split(ln)
        length(f) >= 4 || continue
        br = Symbol(f[1]); n = parse(Int, f[2]); i = parse(Int, f[3]); j = parse(Int, f[4])
        j == n || continue
        key = (br == :b45 ? :full45 : :full1, n)
        push!(get!(out, key, Set{Int}()), i)
    end
    return out
end

function main()
    tlim = length(ARGS) >= 1 ? parse(Float64, ARGS[1]) : 180.0
    pw = load_prewits("dc_witnesses.txt")
    for preds in (:full45, :full1)
        for n in 5:12
            preds == :full1 && n == 12 && continue   # 已证空集
            pre = get(pw, (preds, n), Set{Int}())
            println("#### start $preds $n  (采样见证 $(length(pre)) 对)"); flush(stdout)
            t0 = time()
            run_one(preds, n, tlim; semantics = :exact, eps = 1e-4, prewit = pre)
            println("#### done $preds $n  $(round(time()-t0, digits=1))s"); flush(stdout)
        end
    end
end
main()
