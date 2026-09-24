"""口袋 3 LP 探针：min 机 M0 有 k>=3 件。判危险区是否可行 / 求 max C_A。

变量: t, l0, K, L, pm, pm1, S
关键约束:
  l0 >= 3t (k>=3),  l0 <= 1 (min<=avg),  l0 <= 1-t/m (★★gen+min),
  l0 >= pm (M0 含初始任务),  所有机器 > K-t (含 l0 与 S 聚合),
  K=5L/4, L=pm+pm1, pm >= pm1 >= t,
  可选 jobcap: l0 <= 3(1-2t)  (M0 三件全非大)
输出各 (m, jobcap) 的 max C_A；若 < 5/4 打印对偶证书。
"""
import numpy as np
from scipy.optimize import linprog

T_, L0, K, L, PM, PM1, S = range(7)
NV = 7
NAMES = "t l0 K L pm pm1 S".split()


def probe(m, jobcap=True):
    A, b, names = [], [], []

    def leq(coef, rhs, name):
        row = [0.0] * NV
        for k_, v in coef.items():
            row[k_] = v
        A.append(row); b.append(rhs); names.append(name)

    leq({T_: 1}, sp_val(1, 3), "t<=1/3")            # 口袋3 ⟹ t<=1/3
    leq({L0: -1, T_: 3}, 0, "l0>=3t")
    leq({L0: 1}, 1.0, "l0<=1")
    leq({L0: 1, T_: 1.0 / m}, 1.0, "l0<=1-t/m")      # ★★gen+min
    leq({L0: -1, PM: 1}, 0, "l0>=pm")
    leq({L0: -1, K: 1, T_: -1}, 0, "l0>=K-t")        # fallback 含 M0
    leq({S: -1, K: (m - 1), T_: -(m - 1)}, 0, "S>=(m-1)(K-t)")
    leq({S: -1, L0: (m - 1)}, 0, "S>=(m-1)l0")
    leq({S: 1, L0: 1, T_: 1}, float(m), "★★gen: S<=m-l0-t")
    if jobcap:
        leq({L0: 1, T_: 6}, 3.0, "l0<=3(1-2t)")      # M0 三件全非大
    leq({K: 1, L: -1.25}, 0, "K=5L/4 (a)")
    leq({K: -1, L: 1.25}, 0, "K=5L/4 (b)")
    leq({L: 1, PM: -1, PM1: -1}, 0, "L=pm+pm1 (a)")
    leq({L: -1, PM: 1, PM1: 1}, 0, "L=pm+pm1 (b)")
    leq({PM1: 1, PM: -1}, 0, "pm1<=pm")
    leq({PM: 1}, 1.0, "pm<=1")
    leq({PM1: -1, T_: 1}, 0, "pm1>=t")
    c = [0.0] * NV
    c[L0] = -1.0; c[T_] = -1.0
    res = linprog(c, A_ub=np.array(A), b_ub=np.array(b), bounds=[(0.0, None)] * NV, method="highs")
    return res, names


def sp_val(a, b):
    return a / b


for m in (5, 6, 8, 10, 20, 100):
    for jc in (True, False):
        res, names = probe(m, jc)
        if res.status != 0:
            print(f"m={m} jobcap={jc}: status={res.status}")
            continue
        ca = res.x[L0] + res.x[T_]
        flag = " <<<超5/4" if ca > 1.25 + 1e-9 else ""
        print(f"m={m} jobcap={jc}: max={ca:.6f} t*={res.x[T_]:.4f} l0*={res.x[L0]:.4f}{flag}")
        if flag and m == 5:
            for i, mg in enumerate(res.ineqlin.marginals):
                if abs(mg) > 1e-9:
                    print(f"    {round(-mg,4):8}  {names[i]}")
            print("    极值:", {NAMES[j]: round(res.x[j], 5) for j in range(NV)})
