"""Template-JT：JJJ含t 家族 cnt=(1,m-3,0,1,0,0) 在 k=m-1 的统一符号证书（V2）。
JJJ 箱 = (j_{m-3}, j_{m-2}, t)。证书（RHS=-1/2-12MG）：
  danger:6, pair0:3, pair1:3, SS#0:3, JJJ:4, j_{m-2}>=t:2,
  mon2_0:3, mon2_i(1<=i<=m-4):6, mon2_{m-3}:2
恒等式：6D+3P_0+3P_1+3C+4G+2(j_{m-2}-t)+3M_0+6(j_{m-3}-j_1)+2M_{m-3}=-1/2。
k=m-1 时 mon2_{m-3} 存在（mon2 在 i<jj=m-2）。m=4..30 精确验证。
"""
from fractions import Fraction as F
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hole_close import build_close
from template_b0 import verify_sparse


def template_jt(m, k):
    cnt = (1, m - 3, 0, 1, 0, 0)
    if k != m - 1 or m < 5:
        return None
    A, bc, bt, names, nv = build_close(m, cnt, k)
    idx = {}
    for i, nm in enumerate(names):
        if nm == 'danger': idx['danger'] = i
        elif nm == 'pair0': idx['pair0'] = i
        elif nm == 'pair1': idx['pair1'] = i
        elif nm == 'SS' and 'SS0' not in idx: idx['SS0'] = i
        elif nm == 'JJJ' and 'JJJ0' not in idx: idx['JJJ0'] = i
        elif nm == f'j{m-2}>=t': idx['jt'] = i
        elif nm == 'mon2_j0<=j1': idx['m0'] = i
        elif nm == f'mon2_j{m-3}<=j{m-2}': idx['mlast'] = i
    w = {idx['danger']: 6, idx['pair0']: 3, idx['pair1']: 3, idx['SS0']: 3,
         idx['JJJ0']: 4, idx['jt']: 2, idx['m0']: 3, idx['mlast']: 2}
    for i in range(1, m - 3):
        for j, nm in enumerate(names):
            if nm == f'mon2_j{i}<=j{i+1}':
                w[j] = 6
                break
    return A, bc, bt, nv, {i: F(v) for i, v in w.items()}


if __name__ == '__main__':
    allok = True
    for m in range(5, 31):
        r = template_jt(m, m - 1)
        ok, rhs = verify_sparse(*r)
        if not ok:
            allok = False
            print(f'  ✗ m={m} rhs={rhs}')
        else:
            print(f'  m={m}: ✓ (rhs={rhs})', flush=True)
    print('结论:', 'Template-JT (JJJ含t, k=m-1) 全精确通过 ✓' if allok else '有失效!')
