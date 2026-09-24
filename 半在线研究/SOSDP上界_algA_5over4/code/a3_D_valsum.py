"""a3_ D 块：值语言和界 f(r) 的实测与敌意核查。
引理候选形态：值序最小 r 个 junior（最晚到 r 件后续）的 senior 伙伴之和 ≥ f(r)。
本脚本：角落 LP（无装箱、含保序）顶点采样，实测 f(r) 的归一化值分布，
判定其函数形式（常数倍 r·c？还是含 p,q₁,t 的组合）。
敌意核查：测量的最小值是否恒 ≥ 某干净下界（r·(1−2t)、r·(p−q₁)、或与高端区结构耦合）。
"""
import numpy as np
from scipy.optimize import linprog
import sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fast_lp import rows_fixed

random.seed(23)


def measure(m, k, t0, obj):
    nS = m - 1
    R, nv = rows_fixed(m, (0, 0, nS, 0, 0, 0), k, use_order=True)
    R = [r for r in R if r[3] not in ('SS', 'SJ', 'JJJ', 'JJ')]
    Af = np.array([r for r, _, _, _ in R])
    bf = np.array([float(c0) + float(c1) * t0 for _, c0, c1, _ in R])
    c = np.zeros(nv) if obj is None else obj
    res = linprog(c=c, A_ub=Af, b_ub=bf, bounds=(None, None), method='highs')
    if res.status != 0:
        return None
    x = res.x
    s = x[2:2 + nS]; j = x[2 + nS:2 + 2 * nS]
    return x[0], x[1], s, j


def main():
    print('D 块：值序最小 r 个 junior 的 senior 伙伴和的实测（归一化到 corner 参数）')
    for m in [6, 8, 12]:
        nS = m - 1
        tl = (m - 1) / (4 * (m - 2))
        # 收集全 k 全 t 多样点的 f(r)/r 最小值（平均 senior 下界）
        fmin = {}   # r -> min over points of (最小r个junior的senior和)/r
        fmin_rel = {}  # r -> min of 和/(r·(p−q1)) 等参照
        npts = 0
        for k in range(1, m):
            for t0 in np.linspace(tl + 0.002, 1 / 3, 4):
                for _ in range(8):
                    obj = np.array([random.gauss(0, 1) for _ in range(2 + 2 * nS + 2)])
                    rec = measure(m, k, t0, obj)
                    if rec is None:
                        continue
                    p, t, s, j = rec
                    npts += 1
                    order = np.argsort(j)  # junior 值升序（最小在前=最晚到）
                    for r in range(1, nS + 1):
                        lo = sum(s[order[:r]]) / r
                        fmin[r] = min(fmin.get(r, 9e9), lo)
        print(f'  m={m}（{npts} 点）: 值序最小 r 个 junior 的 senior 均值最小值：')
        print('    ', {r: round(fmin[r], 3) for r in sorted(fmin)})
        # 参照：t 与 1-2t 的尺度
        print(f'     参照尺度：t≈{tl+0.05:.3f}..0.333, 1−2t≈{1-2*(tl+0.05):.3f}..{1-2/3:.3f}')


if __name__ == '__main__':
    main()
