"""U(a) 恒等式的快速全量验证（agent-4）：基于 fast_lp.rows_fixed（去 mon 块 O(m) 行）+ X 行。

恒等式 U(a) 仅用 j1>=t / danger / pair0 / pair1 / srt0..srt_{2a-2} / XSS0 / XTRI——
不含 mon 块/mon2/lowzone/hizone，故 rows_fixed(use_order=False,use_mon=False) 去 caps
+ X 族行即可。纯 Fraction 核对 Aᵀy=0、btᵀy=0、bcᵀy<0。比 build_close 骨架快约 10 倍
（m=50 行数 ~550 vs ~3000），全 26 族一遍 ~2-4 分钟。
"""
import sys, os, time
from fractions import Fraction as F
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fast_lp import rows_fixed

CAPNAMES = {'SS', 'SJ', 'JJJ', 'JJ'}


def build_fast_v4(m, cnt, k):
    """rows_fixed 去 caps + X 必要条件行（XSS/XVOL/XBIG/XSQZ/XVB/XTRI）。返回 (A,bc,bt,names,nv)。"""
    a, b, c, d, e, f = cnt
    nS = m - 1
    R, nv = rows_fixed(m, cnt, k, use_order=False, use_mon=False)
    A = [[F(x) for x in row] for row, _, _, _ in R]
    bc = [c0 for _, c0, _, _ in R]
    bt = [c1 for _, _, c1, _ in R]
    names = [nm for _, _, _, nm in R]
    idx = [i for i, n in enumerate(names) if n not in CAPNAMES]
    A = [A[i] for i in idx]; bc = [bc[i] for i in idx]; bt = [bt[i] for i in idx]
    names = [names[i] for i in idx]

    def vs(i): return 2 + i
    def vj(i): return 2 + nS + i
    it = 1

    def zero(): return [F(0)] * nv
    for i in range(a):
        r = zero(); r[vs(i)] = 1; r[vs(2 * a - 1 - i)] = 1
        A.append(r); bc.append(F(1)); bt.append(F(0)); names.append(f'XSS{i}')
    r = zero()
    for p in range(nS):
        r[vj(p)] = 1
    r[it] = 1
    for i in range(b):
        r[vs(i)] = 1
    A.append(r); bc.append(F(b + d + e + f)); bt.append(F(0)); names.append('XVOL')
    ix = nS - 1 - (c + a + b)
    if 0 <= ix < nS:
        r = zero(); r[vs(ix)] = 1
        A.append(r); bc.append(F(1, 2)); bt.append(F(0)); names.append('XBIG')
    r = zero()
    for i in range(nS):
        r[vs(i)] = 1; r[vj(i)] = 1
    A.append(r); bc.append(F(m - 1)); bt.append(F(-1)); names.append('XSQZ')
    if c == 0:
        for i in range(nS):
            r = zero(); r[vs(i)] = 1
            A.append(r); bc.append(F(1)); bt.append(F(-1)); names.append(f'XVB{i}')
    if d >= 1 and nS >= 2:
        r = zero(); r[it] = 1; r[vj(0)] = 1; r[vj(1)] = 1
        A.append(r); bc.append(F(1)); bt.append(F(0)); names.append('XTRI')
    if e >= 1 and nS >= 2:
        r = zero(); r[vj(0)] = 1; r[vj(1)] = 1
        A.append(r); bc.append(F(1)); bt.append(F(0)); names.append('XJJ')
    return A, bc, bt, names, nv


def U(a):
    rows = [(('j1>=t', 0), F(2)), (('danger', 0), F(6)), (('pair0', 0), F(4)),
            (('pair1', 0), F(2)), (('srt0', 0), F(1))]
    rows += [((f'srt{i}', 0), F(3)) for i in range(1, 2 * a - 1)]
    rows += [(('XSS0', 0), F(3)), (('XTRI', 0), F(4))]
    return rows


def check(m, cnt, k, rw):
    A, bc, bt, names, nv = build_fast_v4(m, cnt, k)
    y = [F(0)] * len(A)
    for (nm, occ), w in rw:
        c_ = 0
        hit = None
        for i, n in enumerate(names):
            if n == nm:
                if c_ == occ:
                    hit = i
                    break
                c_ += 1
        if hit is None:
            return False, f'缺行 {nm}[{occ}]'
        y[hit] = w
    sup = [i for i in range(len(y)) if y[i] != 0]
    for j in range(nv):
        s = sum((A[i][j] * y[i] for i in sup), F(0))
        if s != 0:
            return False, f'A^T y 第{j}列 = {s}'
    if sum((bt[i] * y[i] for i in sup), F(0)) != 0:
        return False, 'bt^T y ≠ 0'
    rhs = sum((bc[i] * y[i] for i in sup), F(0))
    if rhs >= 0:
        return False, f'bc^T y = {rhs} ≥ 0'
    return True, rhs


KEYS = [(0, 1, e, 0) for e in range(6)] + [(0, 2, e, 1) for e in range(4)] + \
       [(0, 3, e, 2) for e in range(2)] + [(1, 2, e, 0) for e in range(5)] + \
       [(1, 3, e, 1) for e in range(3)] + [(1, 4, 0, 2), (2, 3, 0, 0), (2, 3, 1, 0),
       (2, 3, 2, 0), (2, 4, 0, 1)]


def mk_fam(a, c, d, e, f, m):
    b = m - 1 - 2 * a - c
    if b < 0:
        return None
    cnt = (a, b, c, d, e, f)
    assert 2 * a + b + c == m - 1 and b + 3 * d + 2 * e + f == m
    return cnt


if __name__ == '__main__':
    t0 = time.time()
    total_bad = total_case = 0
    for (c, d, e, f) in KEYS:
        a_num = 3 * d + 2 * e + f - 1 - c
        if a_num % 2 or a_num <= 0:
            continue
        a = a_num // 2
        bad = []
        n_case = 0
        for m in range(51):
            cnt = mk_fam(a, c, d, e, f, m)
            if cnt is None:
                continue
            for k in range(2, m):
                n_case += 1
                ok, r = check(m, cnt, k, U(a))
                if not ok:
                    bad.append((m, k, r))
        total_bad += len(bad); total_case += n_case
        print(f'  ({c},{d},{e},{f}) a={a}: {n_case} 案例 '
              f'{"✓" if not bad else f"{len(bad)} 失败 例 {bad[:2]}"} ({time.time()-t0:.0f}s)',
              flush=True)
    print(f'总结: {total_case} 案例, {"razor+邻近全族 U(a) 全通过 ✓" if total_bad == 0 else f"{total_bad} 处失败"}'
          f'  总耗时 {time.time()-t0:.0f}s')
