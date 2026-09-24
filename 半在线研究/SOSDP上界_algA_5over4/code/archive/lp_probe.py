"""LP 探针：口袋1（n=3m-1）静态放松的最大 C_A。

裁决问题：只用计数/体积/顺序/★★ 不等式（不含 best-fit 动态），C_A 能超过 5/4 吗？
- 若 max <= 5/4：纯不等式可证，LP 极值点直接给出证明的不等式骨架；
- 若 max > 5/4：看极值点缺哪条合法约束，定向补。
变量: [t, x, y, z, K, L, pm, pm1, l0, l2, l3, l4, S]
卡片参数: m, a (2件台数; 4件台数同 a; 3件台数 m-1-2a), case_i (l0<=K)
"""
import numpy as np
from scipy.optimize import linprog

# 变量索引
T_, X, Y, Z, K, L, PM, PM1, L0, L2, L3, L4, S = range(13)
NAMES = "t x y z K L pm pm1 l0 l2 l3 l4 S".split()


def probe(m, a, case_i):
    nv = 13
    A, b = [], []

    def leq(coef, rhs):
        row = [0.0] * nv
        for k, v in coef.items():
            row[k] = v
        A.append(row); b.append(rhs)

    # 顺序与基本域
    leq({T_: 1, X: -1}, 0)                 # t <= x
    leq({X: 1, Y: -1}, 0)                  # x <= y
    leq({Y: 1}, 1.0)                       # y <= 1
    leq({Z: 1, Y: 1}, 1.0)                 # z <= 1-y
    leq({Z: 1, T_: 2}, 1.0)                # z <= 1-2t
    leq({T_: 1, Z: -1}, 0)                 # z >= t
    leq({T_: 1}, 0.4)                      # t <= 2/5
    # y 大任务: y > 1-2t  -> 放松为 >=
    leq({Y: -1, T_: -2}, -1.0)             # y >= 1-2t
    # 危险区: l0 >= 5/4 - t （要找 max，放松为 >=）
    leq({L0: -1, T_: -1}, -1.25)           # l0 >= 5/4 - t
    leq({L0: 1, X: -1, Y: -1}, 0)          # l0 <= x+y （l0 = min(x+y, ...) 取 =x+y 为放松）
    leq({L0: -1, X: 1, Y: 1}, 0)           # l0 >= x+y  -> 合并即 l0 = x+y
    # L 与 pm/pm1
    leq({L: 1, PM: -1, PM1: -1}, 0)        # L <= pm+pm1
    leq({L: -1, PM: 1, PM1: 1}, 0)         # L >= pm+pm1 -> L = pm+pm1
    leq({PM1: 1, PM: -1}, 0)               # pm1 <= pm
    leq({PM: 1, T_: 2}, 1.0)               # pm <= 1-2t (p_m != y)
    leq({PM: 1, Y: -1}, 0)                 # pm <= y
    leq({PM1: 1, X: -1}, 0)                # pm1 >= x (x 是后至任务)
    leq({L: -1, PM: -1, X: -1}, 0)         # L >= pm + x -> 其实 L = pm+pm1 >= pm+x 自动
    # K
    leq({K: 1, L: -1.25}, 0)
    leq({K: -1, L: 1.25}, 0)               # K = 5L/4
    # 机器负载: l2/l3/l4 >= K - t (放松), >= l0, >= pm(初始任务)
    for LV in (L2, L3, L4):
        leq({LV: -1, K: 1, T_: -1}, 0)     # lV >= K - t
        leq({LV: -1, L0: 1}, 0)            # lV >= l0
        leq({LV: -1, PM: 1}, 0)            # lV >= pm
    # 件数界
    leq({L2: 1, T_: 4}, 2.0)               # l2 <= 2(1-2t)
    leq({L2: -1, T_: -2}, 0)               # l2 >= 2t
    leq({L3: 1, T_: 6}, 3.0)
    leq({L3: -1, T_: -3}, 0)
    leq({L4: 1, T_: 8}, 4.0)
    leq({L4: -1, T_: -4}, 0)
    # S = a*l2 + a*l4 + (m-1-2a)*l3
    leq({S: 1, L2: -a, L4: -a, L3: -(m - 1 - 2 * a)}, 0)
    leq({S: -1, L2: a, L4: a, L3: (m - 1 - 2 * a)}, 0)
    # ★★: S <= m-1-x+z
    leq({S: 1, X: 1, Z: -1}, m - 1.0)
    # 体积: l0+S >= (3m-1)t
    leq({L0: -1, S: -1, T_: (3 * m - 1)}, 0)
    # case (i): l0 <= K
    if case_i:
        leq({L0: 1, K: -1}, 0)
    # 目标: max l0 + t  ->  min -(l0+t)
    c = [0.0] * nv
    c[L0] = -1.0; c[T_] = -1.0
    bounds = [(0.0, None)] * nv
    res = linprog(c, A_ub=np.array(A), b_ub=np.array(b), bounds=bounds, method="highs")
    if res.status != 0:
        return res.status, None
    return 0, res.x


for m in (4, 5, 6):
    for a in range(0, (m - 1) // 2 + 1):
        for ci in (True, False):
            st, xv = probe(m, a, ci)
            if st != 0:
                print(f"m={m} a={a} case{'i' if ci else 'ii'}: LP {['ok','infeas','unbound','other'][st]}")
            else:
                ca = xv[L0] + xv[T_]
                flag = "  <<< 超 5/4" if ca > 1.25 + 1e-9 else ""
                print(f"m={m} a={a} case{'i' if ci else 'ii'}: max C_A = {ca:.6f}{flag}")
                if ca > 1.25 + 1e-9:
                    print("   ", {NAMES[i]: round(xv[i], 4) for i in range(13)})
