# a4_gap_spot.jl —— 单点验证：各情形的极端 LP 能否顶到 6/5
include("a4_lib.jl")
include("a4_gap_cases.jl")

function spot()
    n = 10; preds = :card
    println("情形 (1,0) 的极端点（m*=1, i=5, j*=10）：")
    v = case_10(n, 10, 1, 5, preds); println("   上界 = ", round(v, digits = 6))
    println("情形 (0,0)（m*=1, j*=10）：")
    v = case_00(n, 10, 1, preds); println("   上界 = ", round(v, digits = 6))
    println("情形 (0,1)（m*=1, jp=5, j*=10）：")
    v = case_01(n, 10, 5, 1, preds); println("   上界 = ", round(v, digits = 6))
end
spot()
