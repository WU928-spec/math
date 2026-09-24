"""口袋 3 LP 卡片：min 机 M0 k>=3 件；其余机器的"小件数机"变体。

卡片 flag:
  sgl: 存在单子机 ℓ1（=初始任务 p_j > K−t, ≥ pm, ≥ l0, ≤ 1）
  two: 存在非大 2 件台 ℓ2 ≤ 2(1−2t)
  big2: 2 件台含大任务 ℓ2 ≤ (1−t) + (1−2t)  [v ≤ 1−t 若 2 箱; 粗放松 ℓ2 ≤ 2−2t]
  l0cap3: l0 <= 3(1−2t)（M0 三件全非大）
  l0big: M0 含大任务 → l0 ≤ 1 + 2(1−2t)（大 + 2 件非大, k>=3）
"""
import numpy as np
from scipy.optimize import linprog

T_, L0, K, L, PM, PM1, S, L1, L2, W_ = range(10)
NV = 10
NAMES = "t l0 K L pm pm1 S l1 l2 w".split()


def probe(m, sgl=False, two=False, big2=False, l0cap3=True, l0big=False):
    A, b, names = [], [], []

    def leq(coef, rhs, name):
        row = [0.0] * NV
        for k_, v in coef.items():
            row[k_] = v
        A.append(row); b.append(rhs); names.append(name)

    leq({T_: 1}, 1 / 3, "t<=1/3")
    leq({L0: -1, T_: 3}, 0, "l0>=3t")
    leq({L0: 1}, 1.0, "l0<=1")
    leq({L0: 1, T_: 1.0 / m}, 1.0, "l0<=1-t/m")
    leq({L0: -1, PM: 1}, 0, "l0>=pm")
    leq({L0: -1, K: 1, T_: -1}, 0, "l0>=K-t")
    leq({S: -1, K: (m - 1), T_: -(m - 1)}, 0, "S>=(m-1)(K-t)")
    leq({S: -1, L0: (m - 1)}, 0, "S>=(m-1)l0")
    leq({S: 1, L0: 1, T_: 1}, float(m), "★★gen: S<=m-l0-t")
    if l0big:
        leq({L0: 1, T_: 4}, 3.0, "l0<=3-4t (M0 含大)")
    elif l0cap3:
        leq({L0: 1, T_: 6}, 3.0, "l0<=3(1-2t)")
    leq({K: 1, L: -1.25}, 0, "K=5L/4 (a)")
    leq({K: -1, L: 1.25}, 0, "K=5L/4 (b)")
    leq({L: 1, PM: -1, PM1: -1}, 0, "L=pm+pm1 (a)")
    leq({L: -1, PM: 1, PM1: 1}, 0, "L=pm+pm1 (b)")
    leq({PM1: 1, PM: -1}, 0, "pm1<=pm")
    leq({PM: 1}, 1.0, "pm<=1")
    leq({PM1: -1, T_: 1}, 0, "pm1>=t")
    if sgl:
        leq({L1: -1, K: 1, T_: -1}, 0, "l1>=K-t")
        leq({L1: -1, L0: 1}, 0, "l1>=l0")
        leq({L1: -1, PM: 1}, 0, "l1>=pm")
        leq({L1: 1}, 1.0, "l1<=1")
        leq({S: -1, L1: 1}, 0, "S>=l1")
    if two:
        leq({L2: -1, L0: 1}, 0, "l2>=l0")
        leq({L2: -1, K: 1, T_: -1}, 0, "l2>=K-t")
        leq({L2: -1, PM: 1}, 0, "l2>=pm")
        leq({L2: 1, T_: 4}, 2.0, "l2<=2(1-2t)")
        leq({S: -1, L2: 1}, 0, "S>=l2")
    if big2:
        leq({L2: -1, L0: 1}, 0, "l2>=l0 (big2)")
        leq({L2: -1, K: 1, T_: -1}, 0, "l2>=K-t (big2)")
        leq({L2: -1, PM: 1}, 0, "l2>=pm (big2)")
        leq({L2: 1, T_: 3}, 2.0, "l2<=2-3t (big2a)")
        leq({S: -1, L2: 1}, 0, "S>=l2 (big2)")
    c = [0.0] * NV
    c[L0] = -1.0; c[T_] = -1.0
    res = linprog(c, A_ub=np.array(A), b_ub=np.array(b), bounds=[(0.0, None)] * NV, method="highs")
    return res, names


variants = [
    ("裸（无小件数机，不可能?）", dict()),
    ("单子机", dict(sgl=True)),
    ("非大2件台", dict(two=True)),
    ("含大2件台", dict(big2=True, l0cap3=False)),
    ("M0含大+非大2件台", dict(two=True, l0cap3=False, l0big=True)),
]
for m in (5, 6, 8, 20):
    for name, kw in variants:
        res, names = probe(m, **kw)
        if res.status != 0:
            print(f"m={m} {name}: status={res.status}")
            continue
        ca = res.x[L0] + res.x[T_]
        flag = " <<<超5/4" if ca > 1.25 + 1e-9 else ""
        print(f"m={m} {name}: max={ca:.6f} t*={res.x[T_]:.4f} l0*={res.x[L0]:.4f}{flag}")
    print()
