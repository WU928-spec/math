"""口袋 2 LP 卡片机：M0 = {p_i} 单子机（初始任务从未被动过）。

关键结构（危险区）: p_i > 5/4 - t >= 0.85 ⟹ p_i 在 OPT 独占一箱 ⟹ ★★-singleton: S <= m-1-t.
卡片:
  sealed:  p_i > K（永远放不下任何任务）
  fit:     p_i <= K（本可放下，但因 best-fit 动力学未被选中 —— 静态放松只看 l1 型）
  small2:  其余机器中存在非大 2 件台 l2 <= 2(1-2t)
  big2:    存在含大任务 2 件台 l2 <= 2-2t（粗放松）
  sgl2:    存在第二台单子机 l1'（也独占 OPT 箱）⟹ S <= m-2-t
"""
import numpy as np
from scipy.optimize import linprog

T_, PI, K, L, PM, PM1, S, L2, L1B = range(9)
NV = 9
NAMES = "t pi K L pm pm1 S l2 l1b".split()


def probe(m, sealed=False, small2=False, big2=False, sgl2=False):
    A, b, names = [], [], []

    def leq(coef, rhs, name):
        row = [0.0] * NV
        for k_, v in coef.items():
            row[k_] = v
        A.append(row); b.append(rhs); names.append(name)

    leq({T_: 1}, 0.4, "t<=2/5")
    leq({T_: -1}, -0.25, "t>1/4 (relax)")
    leq({PI: -1, K: 1, T_: -1}, 0, "pi>=K-t")
    leq({PI: -1, PM: 1}, 0, "pi>=pm")
    leq({PI: 1}, 1.0, "pi<=1")
    if sealed:
        leq({PI: -1, K: 1}, 0, "pi>=K (sealed)")
    else:
        leq({PI: 1, K: -1}, 0, "pi<=K (fit)")
    # OPT 独占箱 ⟹ S <= m-1-t
    leq({S: 1, T_: 1}, float(m - 1), "★★sgl: S<=m-1-t")
    leq({S: -1, PI: (m - 1)}, 0, "S>=(m-1)pi")
    leq({S: -1, K: (m - 1), T_: -(m - 1)}, 0, "S>=(m-1)(K-t)")
    leq({K: 1, L: -1.25}, 0, "K=5L/4 (a)")
    leq({K: -1, L: 1.25}, 0, "K=5L/4 (b)")
    leq({L: 1, PM: -1, PM1: -1}, 0, "L=pm+pm1 (a)")
    leq({L: -1, PM: 1, PM1: 1}, 0, "L=pm+pm1 (b)")
    leq({PM1: 1, PM: -1}, 0, "pm1<=pm")
    leq({PM1: -1, T_: 1}, 0, "pm1>=t")
    leq({PM: 1, PI: -1}, 0, "pm<=pi")
    # 体积: pi + t + S >= (3m-2)t  [n<=3m-2 最大档]
    leq({PI: -1, T_: (3 * m - 3), S: -1}, 0, "VOL: pi+S>=(3m-2)t")
    if small2:
        leq({L2: -1, PI: 1}, 0, "l2>=pi")
        leq({L2: -1, K: 1, T_: -1}, 0, "l2>=K-t")
        leq({L2: 1, T_: 4}, 2.0, "l2<=2(1-2t)")
        leq({S: -1, L2: 1}, 0, "S>=l2")
    if big2:
        leq({L2: -1, PI: 1}, 0, "l2>=pi (big2)")
        leq({L2: -1, K: 1, T_: -1}, 0, "l2>=K-t (big2)")
        leq({L2: 1, T_: 2}, 2.0, "l2<=2-2t (big2)")
        leq({S: -1, L2: 1}, 0, "S>=l2 (big2)")
    if sgl2:
        leq({L1B: -1, PI: 1}, 0, "l1b>=pi")
        leq({L1B: -1, K: 1, T_: -1}, 0, "l1b>=K-t")
        leq({L1B: 1}, 1.0, "l1b<=1")
        leq({S: -1, L1B: 1}, 0, "S>=l1b")
        leq({S: 1, T_: 1}, float(m - 2), "★★sgl2: S<=m-2-t")
    c = [0.0] * NV
    c[PI] = -1.0; c[T_] = -1.0
    res = linprog(c, A_ub=np.array(A), b_ub=np.array(b), bounds=[(0.0, None)] * NV, method="highs")
    return res, names


for m in (4, 5, 6, 8, 20):
    for tag, kw in [("裸", {}), ("sealed", dict(sealed=True)),
                    ("+小2件台", dict(small2=True)), ("+大2件台", dict(big2=True)),
                    ("+第二单子机", dict(sgl2=True)),
                    ("sealed+小2件台", dict(sealed=True, small2=True))]:
        res, names = probe(m, **kw)
        if res.status != 0:
            print(f"m={m} {tag}: status={res.status}")
            continue
        ca = res.x[PI] + res.x[T_]
        flag = " <<<超5/4" if ca > 1.25 + 1e-9 else ""
        print(f"m={m} {tag}: max={ca:.6f} t*={res.x[T_]:.4f} pi*={res.x[PI]:.4f}{flag}")
    print()
