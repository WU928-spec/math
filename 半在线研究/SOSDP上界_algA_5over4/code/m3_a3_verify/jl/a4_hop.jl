# a4_hop.jl —— 用 LP 天花板做"轨迹跳跃"搜索：LP 片内最优实例 → 其轨迹 → 再 LP
include("a4_lib.jl")
include("a4_lp_ceiling.jl")   # 复用 a4c_trace / lp_ceiling（注意它会打印一次，无妨）
