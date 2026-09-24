"""口袋1 修正卡片机：n = 3m-1, m >= 4.

正确计数：M0 = {x,y}（fallback 前 2 件），t 后 3 件；其他机器件数和 = n-3 = 3m-4。
分布 (c2..c8)：Σ c_k = m-1, Σ k·c_k = 3m-4, 各 >= 0, 无 1（单子机=口袋2）。
恒有 c2 >= 1（均值 < 3 鸽巢）。
箱型 (0,1,m-1)：唯一大任务 y，z = y 的箱搭档；其余任务 <= 1-2t。
变量: t x y z K L pm pm1 l0 l[2..8] S   -> 13 + 7 = 20 维
输出每张卡片: max C_A 与 binding 约束。
"""
import numpy as np
from scipy.optimize import linprog
from itertools import product

T_, X, Y, Z, K, L, PM, PM1, L0, S = range(10)
LV = {k: 10 + (k - 2) for k in range(2, 9)}     # l2..l8
NV = 17
NAMES = "t x y z K L pm pm1 l0 S".split() + [f"l{k}" for k in range(2, 9)]


def cards(m):
    """n=3m-1 的其他机器件数分布（计数聚合）：c2..c8, 2..8 件/台, Σc = m-1, Σk·c_k = 3m-4。"""
    sols = []
    total = 3 * m - 4
    for c2 in range(1, m):                       # c2 >= 1 必有
        for c3 in range(0, m):
            for c4 in range(0, m):
                for c5 in range(0, m):
                    for c6 in range(0, m):
                        c7 = c8 = 0
                        cnt = c2 + c3 + c4 + c5 + c6
                        if cnt != m - 1:
                            continue
                        if 2*c2 + 3*c3 + 4*c4 + 5*c5 + 6*c6 != total:
                            continue
                        sols.append((c2, c3, c4, c5, c6, c7, c8))
    return sols


def probe(m, comp, case_i):
    A, b, names = [], [], []

    def leq(coef, rhs, name):
        row = [0.0] * NV
        for k, v in coef.items():
            row[k] = v
        A.append(row); b.append(rhs); names.append(name)

    leq({T_: 1, X: -1}, 0, "t<=x")
    leq({X: 1, Y: -1}, 0, "x<=y")
    leq({Y: 1}, 1.0, "y<=1")
    leq({Z: 1, Y: 1}, 1.0, "z<=1-y")
    leq({Z: 1, T_: 2}, 1.0, "z<=1-2t")
    leq({T_: 1, Z: -1}, 0, "z>=t")
    leq({T_: 1}, 0.4, "t<=2/5")
    leq({Y: -1, T_: -2}, -1.0, "y>=1-2t")
    leq({L0: 1, X: -1, Y: -1}, 0, "l0=x+y (a)")
    leq({L0: -1, X: 1, Y: 1}, 0, "l0=x+y (b)")
    leq({L: 1, PM: -1, PM1: -1}, 0, "L=pm+pm1 (a)")
    leq({L: -1, PM: 1, PM1: 1}, 0, "L=pm+pm1 (b)")
    leq({PM1: 1, PM: -1}, 0, "pm1<=pm")
    leq({PM: 1, T_: 2}, 1.0, "pm<=1-2t")
    leq({PM: 1, Y: -1}, 0, "pm<=y")
    leq({PM1: 1, X: -1}, 0, "pm1>=x")
    leq({K: 1, L: -1.25}, 0, "K=5L/4 (a)")
    leq({K: -1, L: 1.25}, 0, "K=5L/4 (b)")
    leq({L0: -1, K: 1, T_: -1}, 0, "l0>=K-t (fallback 含 M0)")
    # 机器负载界：ℓ_k >= K-t, >= l0, >= pm; ℓ_k <= k(1-2t); ℓ_k >= k·t
    for k in range(2, 9):
        if comp[k - 2] == 0:
            continue
        LK = LV[k]
        leq({LK: -1, K: 1, T_: -1}, 0, f"l{k}>=K-t")
        leq({LK: -1, L0: 1}, 0, f"l{k}>=l0")
        leq({LK: -1, PM: 1}, 0, f"l{k}>=pm")
        leq({LK: 1, T_: 2 * k}, float(k), f"l{k}<=k(1-2t)")
        leq({LK: -1, T_: -k}, 0, f"l{k}>=k*t")
    # S = Σ c_k ℓ_k
    co = {S: 1}
    for k in range(2, 9):
        if comp[k - 2]:
            co[LV[k]] = -comp[k - 2]
    leq(co, 0, "S=dist (a)")
    co2 = {S: -1}
    for k in range(2, 9):
        if comp[k - 2]:
            co2[LV[k]] = comp[k - 2]
    leq(co2, 0, "S=dist (b)")
    # ★★': S <= m-1-x-t+z
    leq({S: 1, X: 1, T_: 1, Z: -1}, m - 1.0, "STAR2': S<=m-1-x-t+z")
    # VOL: l0+S >= (3m-1)t
    leq({L0: -1, S: -1, T_: (3 * m - 1)}, 0, "VOL")
    if case_i:
        leq({L0: 1, K: -1}, 0, "CASEi: l0<=K")
    c = [0.0] * NV
    c[L0] = -1.0; c[T_] = -1.0
    res = linprog(c, A_ub=np.array(A), b_ub=np.array(b), bounds=[(0.0, None)] * NV, method="highs")
    return res, names


for m in (4, 5, 6, 8):
    cs = cards(m)
    for comp in cs:
        for ci in (True, False):
            res, names = probe(m, comp, ci)
            if res.status != 0:
                print(f"m={m} comp={comp[:5]} {'i' if ci else 'ii'}: status={res.status}")
                continue
            ca = res.x[L0] + res.x[T_]
            flag = " <<<" if ca > 1.25 + 1e-9 else ""
            print(f"m={m} comp={comp[:5]} {'i' if ci else 'ii'}: max={ca:.6f} t*={res.x[T_]:.4f}{flag}")
            if ca > 1.25 + 1e-9:
                for i, mg in enumerate(res.ineqlin.marginals):
                    if abs(mg) > 1e-9:
                        print(f"    {round(-mg,4):8}  {names[i]}")
                print("    极值:", {NAMES[j]: round(res.x[j], 4) for j in range(NV) if abs(res.x[j]) > 1e-9})
