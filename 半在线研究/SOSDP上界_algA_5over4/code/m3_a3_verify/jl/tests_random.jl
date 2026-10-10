# tests_random.jl —— 随机对拍（交叉检查，非证明）
#   A. 基例 n <= 5：任意非负非增实例（无 alpha 下界），max C_A3 / C*
#   B. n = 6..9：所有工件 > alpha，归一化 C* <= 1，max C_A3 / C*
include("common.jl")

println("="^78)
println("A. 基例 n = 3,4,5（无工件下界）")
println("="^78)
function run_random_checks()
    rng = MersenneTwister(12345)
    println("="^78); println("A. 基例 n = 3,4,5（无工件下界）"); println("="^78)
    for (n, samples) in [(3, 20000), (4, 20000), (5, 20000)]
        worst = 0.0; witness = Float64[]
        for _ in 1:samples
            p = rand_instance(n, rng; alpha = 0.0, normalize = false)
            r = a3_sim(p)[1] / brute_opt(p, 3)
            r > worst && (worst = r; witness = copy(p))
        end
        println("n = $n   样本 $samples   max C_A3/C* = ", round(worst, digits = 9),
                "   距 c 差 ", round(C_TARGET - worst, digits = 12))
        println("      最坏实例 p = ", round.(witness, digits = 4))
    end
    pt = [1.0, C_TARGET - 1, C_TARGET - 1, C_TARGET - 1]
    println("      紧例 (1, c-1, c-1, c-1) 的比值 = ", round(a3_sim(pt)[1] / brute_opt(pt, 3), digits = 12))

    println("\n" * "="^78); println("B. n = 6..9（所有工件 > alpha，归一化 C* <= 1）"); println("="^78)
    for (n, samples) in [(6, 6000), (7, 6000), (8, 6000), (9, 6000)]
        worst = 0.0; witness = Float64[]
        for _ in 1:samples
            p = rand_instance(n, rng)
            r = a3_sim(p)[1] / brute_opt(p, 3)
            r > worst && (worst = r; witness = copy(p))
        end
        println("n = $n   样本 $samples   max C_A3/C* = ", round(worst, digits = 6),
                (worst <= C_TARGET + 1e-9 ? "   ✓ <= c" : "   ✗ > c"))
        worst > 0.9 * C_TARGET && println("      最坏实例 p = ", round.(witness, digits = 4))
    end
    println("\n完成（随机搜索只作交叉检查；结论以精确 LP 为准）。")
end
run_random_checks()
