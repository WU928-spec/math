"""LP 对偶证书提取：m=4, n=3m-1=11, a=1, case(i)。

ablation 检查（去掉某组约束后 max 是否 > 5/4）+ 提取 binding 约束的对偶乘子，
把 LP 证书法翻译成人类不等式链。
scipy linprog min c^T x s.t. A_ub x <= b_ub; 目标 min -(l0+t)。
"""
import numpy as np
from scipy.optimize import linprog

T_, X, Y, Z, K, L, PM, PM1, L0, L2, L3, L4, S = range(13)
NAMES = "t x y z K L pm pm1 l0 l2 l3 l4 S".split()
DESC = []


def build(m, a, case_i, drop=None):
    nv = 13
    A, b = [], []

    def leq(coef, rhs, name):
        if drop and name in drop:
            return
        row = [0.0] * nv
        for k, v in coef.items():
            row[k] = v
        A.append(row); b.append(rhs); DESC.append(name)

    leq({T_: 1, X: -1}, 0, "t<=x")
    leq({X: 1, Y: -1}, 0, "x<=y")
    leq({Y: 1}, 1.0, "y<=1")
    leq({Z: 1, Y: 1}, 1.0, "z<=1-y")
    leq({Z: 1, T_: 2}, 1.0, "z<=1-2t")
    leq({T_: 1, Z: -1}, 0, "z>=t")
    leq({T_: 1}, 0.4, "t<=2/5")
    leq({Y: -1, T_: -2}, -1.0, "y>=1-2t")
    leq({L0: -1, T_: -1}, -1.25, "DANGER l0>=5/4-t")
    leq({L0: 1, X: -1, Y: -1}, 0, "l0=x+y (a)")
    leq({L0: -1, X: 1, Y: 1}, 0, "l0=x+y (b)")
    leq({L: 1, PM: -1, PM1: -1}, 0, "L=pm+pm1 (a)")
    leq({L: -1, PM: 1, PM1: 1}, 0, "L=pm+pm1 (b)")
    leq({PM1: 1, PM: -1}, 0, "pm1<=pm")
    leq({PM: 1, T_: 2}, 1.0, "pm<=1-2t")
    leq({PM: 1, Y: -1}, 0, "pm<=y")
    leq({PM1: 1, X: -1}, 0, "pm1>=x")
    leq({L: -1, PM: -1, X: -1}, 0, "L>=pm+x")
    leq({K: 1, L: -1.25}, 0, "K=5L/4 (a)")
    leq({K: -1, L: 1.25}, 0, "K=5L/4 (b)")
    for LV, tag in ((L2, "l2"), (L3, "l3"), (L4, "l4")):
        if (LV in (L2, L4)) and a < 1:
            continue                      # 2/4 件台仅在 a>=1 时真实存在
        leq({LV: -1, K: 1, T_: -1}, 0, f"{tag}>=K-t")
        leq({LV: -1, L0: 1}, 0, f"{tag}>=l0")
        leq({LV: -1, PM: 1}, 0, f"{tag}>=pm")
    if a >= 1:
        leq({L2: 1, T_: 4}, 2.0, "l2<=2(1-2t)")
        leq({L2: -1, T_: -2}, 0, "l2>=2t")
        leq({L4: 1, T_: 8}, 4.0, "l4<=4(1-2t)")
        leq({L4: -1, T_: -4}, 0, "l4>=4t")
    leq({L3: 1, T_: 6}, 3.0, "l3<=3(1-2t)")
    leq({L3: -1, T_: -3}, 0, "l3>=3t")
    leq({S: 1, L2: -a, L4: -a, L3: -(m - 1 - 2 * a)}, 0, "S=dist (a)")
    leq({S: -1, L2: a, L4: a, L3: (m - 1 - 2 * a)}, 0, "S=dist (b)")
    leq({S: 1, X: 1, Z: -1}, m - 1.0, "STAR2: S<=m-1-x+z")
    leq({L0: -1, S: -1, T_: (3 * m - 1)}, 0, "VOL: l0+S>=(3m-1)t")
    if case_i:
        leq({L0: 1, K: -1}, 0, "CASEi: l0<=K")
    c = [0.0] * nv
    c[L0] = -1.0; c[T_] = -1.0
    return np.array(A), np.array(b), c, list(DESC)


def run(m, a, case_i, drop=None, verbose=False):
    global DESC
    DESC = []
    A, b, c, names = build(m, a, case_i, drop)
    res = linprog(c, A_ub=A, b_ub=b, bounds=[(0.0, None)] * 13, method="highs")
    if res.status != 0:
        return res.status, None, None
    ca = res.x[L0] + res.x[T_]
    return 0, ca, (res, names) if verbose else None


print("== ablation（去掉哪组约束会突破 5/4）==")
for drop in (None, {"STAR2: S<=m-1-x+z"}, {"VOL: l0+S>=(3m-1)t"},
             {"DANGER l0>=5/4-t"}, {"z<=1-y", "z<=1-2t"},
             {"l2>=K-t", "l3>=K-t", "l4>=K-t"}):
    st, ca, _ = run(4, 1, True, drop)
    label = "完整模型" if not drop else "去掉 " + ",".join(sorted(drop))[:60]
    print(f"  {label}: status={st} max={ca if ca is None else round(ca,6)}")

print("\n== 对偶证书（m=4 a=1 case-i, max=5/4 的 binding 组合）==")
st, ca, (res, names) = run(4, 1, True, verbose=True)
marg = res.ineqlin.marginals
for i, mg in enumerate(marg):
    if abs(mg) > 1e-9:
        print(f"  λ={mg:.6f}  {names[i]}")
print("极值点:", {NAMES[i]: round(res.x[i], 4) for i in range(13)})
EOF_MARKER = None
