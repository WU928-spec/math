"""诊断修正编码的洞：float 快速扫 m=12..20 全 k 全 cnt，并提取 m=12 k=11 可行点。"""
import numpy as np
from scipy.optimize import linprog
from fractions import Fraction as F
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from farkas_fixed import build_fixed, float_cert, MG
from pairing_feasible import bin_count_solutions


def primal_point(m, cnt, k):
    """求原 LP 一个可行点（t 自由变量）。约束形式: A x <= bc + bt*t ⟺ (A - bt*e_t) x <= bc。"""
    A, bc, bt, names, nv = build_fixed(m, cnt, k)
    Af = np.array([[float(x) for x in row] for row in A])
    bcf = np.array([float(x) for x in bc])
    btf = np.array([float(x) for x in bt])
    A2 = Af.copy(); A2[:, 1] -= btf   # 减去 bt*t 列
    res = linprog(c=np.zeros(nv), A_ub=A2, b_ub=bcf, bounds=(None, None), method='highs')
    return res.x if res.status == 0 else None


if __name__ == '__main__':
    print('=== float 洞分布扫描 m=12..20（只列有洞的 k）===')
    for m in range(12, 21):
        cnts = bin_count_solutions(m)
        holes = {}
        for k in range(1, m):
            bad = []
            for cnt in cnts:
                A, bc, bt, names, nv = build_fixed(m, cnt, k)
                if float_cert(A, bc, bt) is None:
                    bad.append(cnt)
            if bad:
                holes[k] = bad
        print(f'  m={m}: ' + (f'洞 k={ {kk: len(v) for kk, v in holes.items()} }' if holes else '无洞'))
        for kk, v in holes.items():
            print(f'      k={kk}: {v[:4]}')
    print()
    print('=== m=12 k=11 cnt=(2,7,0,1,1,0) 可行点 ===')
    x = primal_point(12, (2, 7, 0, 1, 1, 0), 11)
    if x is None:
        print('  无可行点？')
    else:
        nS = 11
        p, t = x[0], x[1]
        s = x[2:2 + nS]; j = x[2 + nS:2 + 2 * nS]
        am, q1 = x[2 + 2 * nS], x[2 + 2 * nS + 1]
        K = 1.25 * (am + q1)
        print(f'  p={p:.4f} t={t:.4f} p+t={p+t:.4f}  K={K:.4f}  am={am:.4f} q1={q1:.4f}')
        print(f'  seniors: {np.round(s, 4)}')
        print(f'  juniors: {np.round(j, 4)}')
        print(f'  pair 余量 s+j-p: {np.round(s + j - p, 4)}')
        print(f'  s+t-K(应>0): {np.round(s + t - K, 4)}')
        tl = (12 - 1) / (4 * (12 - 2))
        print(f'  窗口下界 tl={tl:.4f}, t 在窗口内? {tl < t <= 1/3}')
