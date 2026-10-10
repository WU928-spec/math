# run_all.jl —— 依次运行全部测试
# 用法：julia --project=. run_all.jl
for f in ["tests_bounds_m3.jl", "tests_random.jl", "tests_base_case_m3.jl", "tests_m4_coords.jl"]
    println("\n", "█"^78, "\n█ 运行 ", f, "\n", "█"^78)
    include(f)
end
println("\n全部测试运行完毕。")
