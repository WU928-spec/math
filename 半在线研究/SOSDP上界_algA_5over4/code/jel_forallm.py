"""JEL ③微观检验：下降路径的模式随 m 平移不变性。
同形状值族（排序后几何相近），箱数 m=4,5,6——比较路径的模式签名
（交换类型序列，物品按值序编号）是否一致。
若一致 ⟹ regime=模式类，m-无关，∀m 簿记可行。
"""
import sys
sys.path.insert(0, '/Users/a123456/math/research/2026-09-19_algA_5over4/code')
from jel_path import descent_path, idx_struct


def trial(base, m):
    """base: 值形状（升序列表，长度=m 或 m+1）；返回路径模式签名。"""
    items = sorted([(v, i) for i, v in enumerate(base)])
    bins, path = descent_path(items, m)
    return tuple(path), idx_struct(bins)


# 形状：一件大 + 其余同值（角落"t 独小"形态的简化）
for m in [4, 5, 6]:
    base = [0.62] + [0.30] * (m - 2) + [0.28]
    path, st = trial(base, m)
    print(f'm={m}: n={len(base)} 路径={path}  结构={st}')
print()
# 形状：双大+同值小件
for m in [4, 5, 6]:
    base = [0.60, 0.58] + [0.29] * (m - 3) + [0.27]
    path, st = trial(base, m)
    print(f'm={m}: n={len(base)} 路径={path}  结构={st}')
