"""统一符号证书：对 a>=1, d>=1, b>=1, b+2<=m-2, k>=b+2 的 (cnt,k)，
不显式解 LP，直接构造 Farkas 证书 y 并用 Fraction 精确验证
（A^T y=0, bt^T y=0, bc^T y<0, y>=0）。

证书模板（权，未归一化；RHS = -1/2 - 12*MG < 0）：
  danger        : 6      （p+t > 5/4）
  pair_0, pair_1: 3 each （s_i+j_i >= p，取第一个 SS 箱的两台机）
  SS 箱 #0      : 3      （s_0+s_1 <= 1）
  JJJ 箱 #0     : 4      （j_b+j_{b+1}+j_{b+2} <= 1，b = #SJ 箱数）
  j_{b+1}>=t    : 2
  j_{b+2}>=t    : 4
  mon2_0        : 3      （j_0 <= j_1）
  mon2_i, 1<=i<=b-1 : 6
  mon2_b        : 2      （j_b <= j_{b+1}）
恒等式（每项括号均为合法非负量，求和 = -1/2，矛盾）：
  6(p+t-5/4)+3(s_0+j_0-p)+3(s_1+j_1-p)+3(1-s_0-s_1)+4(1-j_b-j_{b+1}-j_{b+2})
  +2(j_{b+1}-t)+4(j_{b+2}-t)+3(j_1-j_0)+6(j_b-j_1)+2(j_{b+1}-j_b) = -1/2
适用条件：a>=1（有 SS 箱）、d>=1（有 JJJ 箱）、1<=b 且 b+2<=m-2（JJJ#0 不含 t）、
  k>=b+2（mon2_b 行存在）。m=12..20 的全部洞（三个家族）均满足。
"""
from fractions import Fraction as F
import sys, os, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from farkas_fixed import build_fixed, MG
from hole_close import build_close
from pairing_feasible import bin_count_solutions


def template_weights(m, cnt, k):
    """返回 {row_index: weight}（未归一化 Fraction），不适用返回 None。"""
    a, b, c, d, e, f = cnt
    nS = m - 1
    if a < 1 or d < 1 or b < 1:
        return None
    if b + 2 > m - 2:      # JJJ#0 含 t，模板不适用
        return None
    if k < b + 2:          # mon2_b 不存在（mon2 只在 i<jj=k-1）
        return None
    A, bc, bt, names, nv = build_close(m, cnt, k)
    idx = {}
    first_SS = first_JJJ = None
    for i, nm in enumerate(names):
        if nm == 'danger':
            idx['danger'] = i
        elif nm == 'pair0':
            idx['pair0'] = i
        elif nm == 'pair1':
            idx['pair1'] = i
        elif nm == 'SS' and first_SS is None:
            first_SS = i
        elif nm == 'JJJ' and first_JJJ is None:
            first_JJJ = i
        elif nm == f'j{b+1}>=t':
            idx['jb1'] = i
        elif nm == f'j{b+2}>=t':
            idx['jb2'] = i
        elif nm == 'mon2_j0<=j1':
            idx['m0'] = i
        elif nm == f'mon2_j{b}<=j{b+1}':
            idx['mb'] = i
    w = {idx['danger']: 6, idx['pair0']: 3, idx['pair1']: 3, first_SS: 3,
         first_JJJ: 4, idx['jb1']: 2, idx['jb2']: 4, idx['m0']: 3, idx['mb']: 2}
    for i in range(1, b):
        for j, nm in enumerate(names):
            if nm == f'mon2_j{i}<=j{i+1}':
                w[j] = 6
                break
    return A, bc, bt, nv, {i: F(v) for i, v in w.items()}


def verify_y(A, bc, bt, nv, w):
    """精确验证：A^T y=0, bt^T y=0, bc^T y<0, y>=0。返回 (ok, rhs)。"""
    y = [w.get(i, F(0)) for i in range(len(A))]
    if any(v < 0 for v in y):
        return False, None
    for j in range(nv):
        if sum(A[i][j] * y[i] for i in range(len(A))) != 0:
            return False, None
    if sum(bt[i] * y[i] for i in range(len(A))) != 0:
        return False, None
    rhs = sum(bc[i] * y[i] for i in range(len(A)))
    return (rhs < 0), rhs


def covered(cnt, m, k):
    a, b, c, d, e, f = cnt
    return a >= 1 and d >= 1 and b >= 1 and b + 2 <= m - 2 and k >= b + 2


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'exact'
    if cmd == 'exact':
        # 精确 Fraction 验证：小 m 全量，大 m 抽样（含已知洞家族模式）
        import random
        allok = True
        for m in [12, 13, 14, 18, 19, 20, 25, 30, 40, 60]:
            cases = []
            for cnt in bin_count_solutions(m):
                for k in range(1, m):
                    if covered(cnt, m, k):
                        cases.append((cnt, k))
            if m > 20 and len(cases) > 150:
                random.seed(m)
                fam = [c for c in cases if c[0] in
                       [(2, m - 5, 0, 1, 1, 0), (3, m - 7, 0, 1, 2, 0), (3, m - 8, 1, 2, 1, 0)]]
                cases = sorted(set(fam + random.sample(cases, 150)))
            nok = 0
            rhss = set()
            for cnt, k in cases:
                r = template_weights(m, cnt, k)
                ok, rhs = verify_y(*r)
                rhss.add(rhs)
                if ok:
                    nok += 1
                else:
                    allok = False
                    print(f'  ✗ m={m} cnt={cnt} k={k} 证书失效 (rhs={rhs})')
            print(f'  m={m}: {nok}/{len(cases)} 精确证书通过, rhs∈{sorted(rhss)[:2]}', flush=True)
        print('结论:', '统一符号证书全部精确通过 ✓' if allok else '有失效!')
    elif cmd == 'struct':
        # 结构扫描：m=4..60，统计 (covered cnt,k) 占比 + 列出未被覆盖的 cnt 类
        for m in [12, 18, 20, 30, 40, 60]:
            cnts = bin_count_solutions(m)
            tot = cov = 0
            uncov = set()
            for cnt in cnts:
                a, b, c, d, e, f = cnt
                for k in range(1, m):
                    tot += 1
                    if covered(cnt, m, k):
                        cov += 1
                    else:
                        uncov.add(('a=0' if a == 0 else '') + ('d=0' if d == 0 else '')
                                  + ('b=0' if b == 0 else '') + ('k<b+2' if k < b + 2 else '')
                                  + ('JJJ含t' if b + 2 > m - 2 else ''))
            print(f'  m={m}: 覆盖 {cov}/{tot} ({100*cov/tot:.1f}%), 未覆盖类型 {sorted(uncov)}')
    elif cmd == 'holes':
        # m=12..20 已知洞：逐一检查被模板覆盖
        from hole_close import holes_of
        for m in range(12, 21):
            for cnt, k in holes_of(m):
                print(f'  m={m} k={k} cnt={cnt}: covered={covered(cnt, m, k)}')
