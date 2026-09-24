"""口袋 2 角落 LP v2：件数 × 大任务计数 × 箱型 联合约束。

变量(连续放松): t, pi, K, L, pm, pm1, S, sg(单子机数), c2(2件台数), c3(3件台数),
              B(大任务数), b1, b2(箱型; b3 = m-b1-b2), Vsmall(非大任务总体积)
核心新约束:
  - 无大任务的机器件数 ≥ ceil((5/4-t)/(1-2t))（聚合放松: 负载 ≤ count·(1-2t)）
  - 大任务数 B >= sg + c2；B <= 2*b2 + b1
  - 箱型: b1+2*b2+3*b3 >= n（容量）, b1+b2+b3 = m
  - 每台含大 2 件机负载 ≤ (1-t)+(1-2t)=2-3t；单子机 = p_j ∈ [pi, 1]
目标: max pi + t
"""
import numpy as np
from scipy.optimize import linprog

# t pi K L pm pm1 S sg c2 c3 B b1 b2 n
IDX = list(range(14))
T_, PI, K, L, PM, PM1, S, SG, C2, C3, B, B1, B2, N_ = IDX
NAMES = "t pi K L pm pm1 S sg c2 c3 B b1 b2 n".split()


def probe(m, hard3=False):
    """hard3: t > 1/3（2 箱段）"""
    A, b, names = [], [], []

    def leq(coef, rhs, name):
        row = [0.0] * 14
        for k_, v in coef.items():
            row[k_] = v
        A.append(row); b.append(rhs); names.append(name)

    tlo = 1 / 3 if hard3 else 0.2501
    thi = 0.4
    leq({T_: -1}, -tlo, "t>=tlo")
    leq({T_: 1}, thi, "t<=2/5")
    leq({PI: -1, K: 1, T_: -1}, 0, "pi>=K-t")
    leq({PI: 1}, 1.0, "pi<=1")
    leq({PI: -1, T_: 1}, -1.25, "danger pi>5/4-t (relax >=)")
    leq({K: 1, L: -1.25}, 0, "K=5L/4a"); leq({K: -1, L: 1.25}, 0, "K=5L/4b")
    leq({L: 1, PM: -1, PM1: -1}, 0, "L=pm+pm1a"); leq({L: -1, PM: 1, PM1: 1}, 0, "L=pm+pm1b")
    leq({PM1: 1, PM: -1}, 0, "pm1<=pm")
    leq({PM1: -1, T_: 1}, 0, "pm1>=t")
    leq({PM: 1, PI: -1}, 0, "pm<=pi")
    leq({PM1: 1, PI: -4, PM: 5}, 0, "pi+pm1>K")
    # S 链
    leq({S: 1, T_: 1}, float(m - 1), "S<=m-1-t (★★sgl)")
    leq({S: -1, PI: (m - 1)}, 0, "S>=(m-1)pi")
    leq({S: -1, K: (m - 1), T_: -(m - 1)}, 0, "S>=(m-1)(K-t)")
    # 件数: sg + c2 + c3 = m-1 (c3 = >=3 件台);  n >= 2 + sg + 2c2 + 3c3
    leq({SG: 1, C2: 1, C3: 1}, float(m - 1), "sg+c2+c3=m-1 (a)")
    leq({SG: -1, C2: -1, C3: -1}, -(m - 1.0), "sg+c2+c3=m-1 (b)")
    leq({N_: -1, SG: 1, C2: 2, C3: 3}, -2.0, "n>=2+sg+2c2+3c3")
    # 箱容量: t<=1/3 时 n <= b1+2b2+3b3 = 3m-2b1-b2;  t>1/3 时 b3=0, n <= 2m-b1
    if hard3:
        leq({N_: 1, B1: 1}, 2.0 * m, "n<=2m-b1 (t>1/3)")
    else:
        leq({N_: 1, B1: 2, B2: 1}, 3.0 * m, "n<=3m-2b1-b2")
    # 大任务: B >= sg + c2 ; B <= b1 + 2 b2
    leq({B: -1, SG: 1, C2: 1}, 0, "B>=sg+c2")
    leq({B: 1, B1: -1, B2: -2}, 0, "B<=b1+2b2")
    # b1 <= sg(大单子机独占箱)…粗放松不加
    # 直接编码两个下界（min 链与 fallback 链均已在上方）
    c = [0.0] * 14
    c[PI] = -1; c[T_] = -1
    res = linprog(c, A_ub=np.array(A), b_ub=np.array(b), bounds=[(0.0, None)] * 14, method="highs")
    return res, names


for hard3 in (False, True):
    for m in (4, 5, 6, 8, 11, 20):
        res, names = probe(m, hard3)
        if res.status != 0:
            print(f"m={m} hard3={hard3}: status={res.status}")
            continue
        ca = res.x[PI] + res.x[T_]
        flag = " <<<超5/4" if ca > 1.25 + 1e-9 else ""
        print(f"m={m} hard3={hard3}: max={ca:.6f} t*={res.x[T_]:.4f} pi*={res.x[PI]:.4f}{flag}")
        if flag and m in (4, 11):
            for i, mg in enumerate(res.ineqlin.marginals):
                if abs(mg) > 1e-9:
                    print(f"    {round(-mg,4):8}  {names[i]}")
            print("   极值:", {NAMES[j]: round(res.x[j], 4) for j in range(14)})
    print()
