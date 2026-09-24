"""razor 带符号恒等式族的精确验证器（agent-4）。

恒等式族（候选，从证书支撑解码）：
  IDA-k2（shape A=(1,m−3,0,1,0,0) @ k=2，9 行）：
    5·danger + 3·pair0 + 2·pair1 + 1·(am<=s1) + 2·(t<=q1) + 1·(q1<=am) + 1·(q1<=j1)
    + 3·XSS0(s₀+s₁≤1) + 3·XTRI(t+j₀+j₁≤1) = −1/4 − 10·MG
  IDB-k4（shape B=(2,m−5,0,1,1,0) @ k=4，8 行，权重 2,6,4,2,4,3,3,4 待解码核）。
验证：在 build_v4 行集上按名字定位行索引，Fraction 精确核 Aᵀy=0 / btᵀy=0 / bcᵀy<0 / y≥0，
m=4..50 全 k 适用处。名字去重按出现序。
"""
import sys, os
from fractions import Fraction as F
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a4_razor_symbolic import build_v4


def find_rows(names, spec):
    """spec: [(名字, 第几次出现), ...] -> [索引]。严格按出现序匹配。"""
    used = [0] * len(spec)
    out = []
    for nm, occ in spec:
        cnt_ = 0
        hit = None
        for i, n in enumerate(names):
            if n == nm:
                if cnt_ == occ:
                    hit = i
                    break
                cnt_ += 1
        if hit is None:
            raise KeyError(f'行 {nm}[{occ}] 不存在')
        out.append(hit)
    return out


def check_identity(m, cnt, k, rowspec_weights, verbose=False):
    """rowspec_weights: [((名字,occ), 权重Fraction)]。返回 (ok, rhs)。"""
    A, bc, bt, names, nv = build_v4(m, cnt, k)
    y = [F(0)] * len(A)
    try:
        for (nm, occ), w in rowspec_weights:
            y[find_rows(names, [(nm, occ)])[0]] = w
    except KeyError as e:
        return False, f'缺行 {e}'
    for j in range(nv):
        s = sum((A[i][j] * y[i] for i in range(len(y)) if y[i] != 0), F(0))
        if s != 0:
            return False, f'A^T y 第{j}列 = {s}'
    s = sum((bt[i] * y[i] for i in range(len(y)) if y[i] != 0), F(0))
    if s != 0:
        return False, f'bt^T y = {s}'
    rhs = sum((bc[i] * y[i] for i in range(len(y)) if y[i] != 0), F(0))
    if rhs >= 0:
        return False, f'bc^T y = {rhs} >= 0'
    if verbose:
        print(f'    m={m} cnt={cnt} k={k}: rhs = {rhs}')
    return True, rhs


IDA_K2 = [(('danger', 0), F(5)), (('pair0', 0), F(3)), (('pair1', 0), F(2)),
          (('am<=s1', 0), F(1)), (('t<=q1', 0), F(2)), (('q1<=am', 0), F(1)),
          (('q1<=j1', 0), F(1)), (('XSS0', 0), F(3)), (('XTRI', 0), F(3))]

IDB_K4 = [(('j1>=t', 0), F(2)), (('danger', 0), F(6)), (('pair0', 0), F(4)),
          (('pair1', 0), F(2)), (('srt0', 0), F(4)), (('srt1', 0), F(3)),
          (('XSS1', 0), F(3)), (('XTRI', 0), F(4))]

if __name__ == '__main__':
    import time
    t0 = time.time()
    print('== IDA-k2: shape A (1,m−3,0,1,0,0) @ k=2, m=4..50 ==')
    bad = 0
    for m in range(4, 51):
        ok, r = check_identity(m, (1, m - 3, 0, 1, 0, 0), 2, IDA_K2,
                               verbose=(m in (4, 12, 30, 50)))
        if not ok:
            bad += 1
            print(f'  失败 m={m}: {r}')
    print(f'  {"全通过 ✓ (47 个 m)" if bad == 0 else f"{bad} 处失败"}  rhs={r}')
    print('== IDB-k4: shape B (2,m−5,0,1,1,0) @ k=4, m=6..50 ==')
    bad = 0
    for m in range(6, 51):
        ok, r = check_identity(m, (2, m - 5, 0, 1, 1, 0), 4, IDB_K4,
                               verbose=(m in (6, 12, 30, 50)))
        if not ok:
            bad += 1
            print(f'  失败 m={m}: {r}')
    print(f'  {"全通过 ✓ (45 个 m)" if bad == 0 else f"{bad} 处失败"}  rhs={r}')
    print(f'({time.time()-t0:.0f}s)')
