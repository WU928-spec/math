"""口袋 2 角落的权重函数元-LP。

想法: 找权函数 w(x) 使:
  (B) a+b <= 1 (OPT 箱可行)   ⟹ w(a)+w(b) <= W      （对全部格点, 含三件的 3-bin 版）
  (M) u+v > p_1, v in [t, 2t) ⟹ w(u)+w(v) >= V      （机器侧 2 件台）
计数: Σ_jobs w = Σ_machines w > (m-1)V ; Σ_jobs w <= m·W - [w(p1) 独占箱省了...]
      (m-1)V < (m-1)W + (W - w(p1) - w(t))  ⟹ 若 V > W 则大 m 全部杀死。
网格 x in [t, 1]，取 N 格。max V - W。
"""
import numpy as np
from scipy.optimize import linprog


def probe(t, p1, N=40, verbose=False):
    # 格点: x_g = t + g*(1-t)/N, g=0..N
    G = N + 1
    xs = np.array([t + g * (1 - t) / N for g in range(G)])
    # 变量: w_0..w_{G-1}, W, V
    nv = G + 2
    Wi, Vi = G, G + 1
    A, b = [], []
    lw, up = 1e-6, 1.0  # 权值域，无妨归一

    def leq(row, rhs):
        A.append(row); b.append(rhs)

    for g1 in range(G):
        for g2 in range(g1, G):
            x1, x2 = xs[g1], xs[g2]
            rowW = [0.0] * nv; rowW[g1] = 1; rowW[g2] = 1; rowW[Wi] = -1
            rowV = [0.0] * nv; rowV[g1] = -1; rowV[g2] = -1; rowV[Vi] = 1
            if x1 + x2 <= 1 + 1e-12:          # 箱可行 -> <= W
                leq(rowW, 0)
            if x2 < 2 * t - 1e-12 and x1 + x2 > p1 + 1e-12:   # 机器侧 (v 在 [t,2t) 窄带; u>=v 由对称)
                leq(rowV, 0)
    # 3 件箱: a+b+c <= 1 -> w(a)+w(b)+w(c) <= W
    for g1 in range(G):
        for g2 in range(g1, G):
            for g3 in range(g2, G):
                if xs[g1] + xs[g2] + xs[g3] <= 1 + 1e-12:
                    row = [0.0] * nv
                    row[g1] = 1; row[g2] = 1; row[g3] = 1; row[Wi] = -1
                    leq(row, 0)
    # 归一化: W <= 1
    row = [0.0] * nv; row[Wi] = 1; leq(row, 1.0)
    # w >= 0 (bounds), w 单调不增(可选, 不强制)
    c = [0.0] * nv; c[Vi] = -1.0; c[Wi] = 1.0   # max V - W
    bounds = [(0.0, None)] * G + [(0.0, None), (0.0, None)]
    res = linprog(c, A_ub=np.array(A), b_ub=np.array(b), bounds=bounds, method="highs")
    if res.status != 0:
        return None, res.status
    return (res.x[Vi], res.x[Wi], res.x[:G], xs), 0


# 角落参数区: t in (1/4, 1/3], p1 in (5/4-t, 1 - t/(m-1)]  -- 取代表点
for t in (0.26, 0.29, 1/3):
    for p1 in (0.9, 0.95):
        out, st = probe(t, p1)
        if st != 0:
            print(f"t={t:.4f} p1={p1}: LP status {st}")
            continue
        V, W, w, xs = out
        print(f"t={t:.4f} p1={p1}: V={V:.4f} W={W:.4f} V-W={V-W:+.4f} {'<<< 有证书!' if V > W + 1e-9 else ''}")
        if V > W + 1e-9:
            print("   w 曲线:", np.round(w, 3))
