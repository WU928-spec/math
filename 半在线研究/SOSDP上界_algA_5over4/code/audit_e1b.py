"""E1b: 加强版装箱搜索——口袋2无bins松弛中是否存在可装箱点（角落的声音松弛）。
随机目标采样顶点 + m=12 k=11 已知静态自洽洞的装箱复核。
"""
from fractions import Fraction as F
import numpy as np
from scipy.optimize import linprog
import sys, os, random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audit_constraints import build_p2, primal_feasible, pack_exact, bin_type_of
from pairing_feasible import bin_count_solutions
from farkas_fixed import build_fixed, float_cert

random.seed(20260921)


def packable_points(m, k, nrand=40, verbose=True):
    nS = m - 1
    tl = (m - 1) / (4 * (m - 2))
    A, bc, bt, names, nv = build_p2(m, (0, 0, nS, 0, 0, 0), k, drop=('SS', 'SJ', 'JJJ', 'JJ'))
    found = []
    for t0 in np.linspace(tl + 0.002, 1 / 3, 5):
        objs = [None]
        for _ in range(nrand):
            objs.append(np.array([random.gauss(0, 1) for _ in range(nv)]))
        for obj in objs:
            x, _ = primal_feasible(A, bc, bt, t0, nv, obj=obj)
            if x is None:
                continue
            p, tt = x[0], x[1]
            s = x[2:2 + nS]; j = x[2 + nS:2 + 2 * nS]
            items = [F(str(v)).limit_denominator(10**6) for v in list(s) + list(j) + [tt]]
            seniors = set(F(str(v)).limit_denominator(10**6) for v in s)
            bins = pack_exact(items, m - 1)
            if bins is not None:
                bt_ = bin_type_of(bins, seniors)
                found.append((t0, p, tt, bt_, list(s), list(j)))
    if verbose and found:
        t0, p, tt, bt_, s, j = found[0]
        print(f'  ★ m={m} k={k}: 找到可装箱点! t={t0:.4f} p={p:.4f} p+t={p+tt:.4f} 箱型={bt_}')
        print(f'      s={np.round(s,4)}')
        print(f'      j={np.round(j,4)}')
    return found


def hole_m12():
    """m=12 k=11 已知静态自洽洞（NOTES: cnt=(2,7,0,1,1,0)）的装箱复核。"""
    m, k = 12, 11
    cnts = bin_count_solutions(m)
    feas = []
    for cnt in cnts:
        A, bc, bt, names, nv = build_fixed(m, cnt, k)
        if float_cert(A, bc, bt) is None:
            feas.append(cnt)
    print(f'm=12 k=11: 固定分组 LP 可行的 cnt = {feas}')
    # 抓一个可行点做装箱检查（该点满足固定分组 cnt 的 caps ⟹ 按定义可装箱）
    for cnt in feas:
        A, bc, bt, names, nv = build_fixed(m, cnt, k)
        tl = (m - 1) / (4 * (m - 2))
        for t0 in np.linspace(tl + 0.002, 1 / 3, 4):
            x, _ = primal_feasible(A, bc, bt, t0, nv)
            if x is None:
                continue
            p, tt = x[0], x[1]
            nS = m - 1
            s = x[2:2 + nS]; j = x[2 + nS:2 + 2 * nS]
            print(f'  cnt={cnt} t={t0:.4f}: p={p:.4f} p+t={p+tt:.4f}')
            print(f'    s={np.round(s,4)}')
            print(f'    j={np.round(j,4)}')
            items = [F(str(v)).limit_denominator(10**6) for v in list(s) + list(j) + [tt]]
            seniors = set(F(str(v)).limit_denominator(10**6) for v in s)
            bins = pack_exact(items, m - 1)
            print(f'    装箱: {"可行 " + str(bin_type_of(bins, seniors)) if bins else "不可行（连该洞的固定分组点也不装箱?）"}')
            break


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if cmd in ('all', 'search'):
        total = 0
        for m in [6, 7, 8, 9, 10]:
            for k in range(1, m):
                f = packable_points(m, k)
                total += len(f)
        print(f'汇总：随机目标采样下可装箱点总数 = {total}')
    if cmd in ('all', 'hole'):
        hole_m12()
