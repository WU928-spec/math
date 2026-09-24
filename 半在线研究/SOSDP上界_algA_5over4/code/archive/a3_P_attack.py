"""a3_ (P) 正面攻坚：JJJ 侧判定 LP。
装箱可行 ⟹ 计数恒等式 d=1+c+f>=1 ⟹ 存在三件 junior 类件同箱和<=1 ⟹ min三件和<=1。
故若角落约束下 min_{u<v<w}(池三件和) > 1 ⟹ JJJ 死 ⟹ 该 (m,k) 的 (P) 闭合。
本 LP：角落约束（fast_lp 无装箱版 + 保序）+ z <= 各池三件和 ⟹ maximize z。
max z > 1 ⟹ 所有三件和 > 1 ⟹ JJJ 不可能。
"""
import numpy as np
from scipy.optimize import linprog
from fractions import Fraction as F
import sys, os, itertools, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fast_lp import rows_fixed

MG = F(1, 10000)


def build_z(m, k, use_order=True):
    """rows_fixed（去装箱帽——rows_fixed 里装箱帽在末尾 SS/SJ/JJJ/JJ 行）+ z 变量 + 三件和约束。
    rows_fixed 的行含装箱帽（名 SS/SJ/JJJ/JJ）——剔除。"""
    a_dummy = (0, 0, m - 1, 0, 0, 0)  # cnt 只影响装箱帽行，全部剔除
    R, nv0 = rows_fixed(m, a_dummy, k, use_order=use_order)
    R = [r for r in R if r[3] not in ('SS', 'SJ', 'JJJ', 'JJ')]
    nS = m - 1
    iz = nv0  # z 的新变量索引
    nv = nv0 + 1
    # 池 = juniors（索引 2+nS+i）+ t（索引 1）
    pool = [2 + nS + i for i in range(nS)] + [1]
    A, b = [], []
    for row, c0, c1, nm in R:
        # 展开成固定 t 形式在调用处做；这里保留 (A, bc, bt)
        A.append((list(row) + [0.0], c0, c1, nm))
    # z <= 三件和：z - j_u - j_v - j_w <= 0
    for u, v, w in itertools.combinations(pool, 3):
        row = [0.0] * nv
        row[iz] = 1.0; row[u] = -1.0; row[v] = -1.0; row[w] = -1.0
        A.append((row, F(0), F(0), 'zcap'))
    return A, nv, iz


def max_z(m, k, t0, use_order=True):
    A, nv, iz = build_z(m, k, use_order)
    Af = np.array([r for r, _, _, _ in A])
    bf = np.array([float(c0) + float(c1) * t0 for _, c0, c1, _ in A])
    c = np.zeros(nv); c[iz] = -1.0
    res = linprog(c=c, A_ub=Af, b_ub=bf, bounds=(None, None), method='highs')
    if res.status != 0:
        return None
    return -res.fun


def main():
    print('(P) JJJ 侧判定：max z（min三件和的下界最大值）>1 ⟹ JJJ 死 ⟹ (P) 闭合')
    t_start = time.time()
    for m in [6, 8, 10, 12]:
        tl = (m - 1) / (4 * (m - 2))
        row = []
        for k in range(1, m):
            worst = -9
            for t0 in np.linspace(tl + 0.002, 1 / 3, 6):
                z = max_z(m, k, t0)
                if z is not None and z > worst:
                    worst = z
            row.append(worst)
        tags = ['%.3f%s' % (w, '✗JJJ活' if 0.99 < w <= 1.0001 else ('✓死' if w > 1 else '·')) for w in row]
        print(f'  m={m}: max z per k = {["%.3f" % w for w in row]}')
        print(f'         {tags}')
    print(f'({time.time()-t_start:.0f}s)')


if __name__ == '__main__':
    main()
