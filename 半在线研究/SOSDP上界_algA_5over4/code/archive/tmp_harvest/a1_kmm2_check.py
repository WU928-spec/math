"""a3_endpoint_symbolic k=m-2 恒等式独立抽验：m=6 与 m=9（Fraction 精确）。"""
import sys
sys.path.insert(0, 'code')
from fractions import Fraction as F
import a1_value_lp2 as V

MG_ = F(1, 10000)
for m in [6, 9]:
    nS = m - 1
    cnt = (1, m - 3, 0, 1, 0, 0)
    A, bc, bt, names, leg, nv = V.build(m, cnt, use_b4=False, use_sjrev=False)
    IP, IAM, IQ1 = 0, 1, 2
    vs = lambda r: 3 + (r - 1); vj = lambda r: 3 + nS + (r - 1)
    A, bc, bt = list(A), list(bc), list(bt)
    def con(row, c0, c1, nm):
        A.append([F(x) for x in row]); bc.append(F(c0)); bt.append(F(c1)); names.append(nm)
    k = m - 2
    for i in range(1, k + 1):
        row = [F(0)] * nv; row[IP] = 1; row[vs(i)] = -1; row[vj(nS - k + i)] = -1
        con(row, -MG_, 0, f'A5_{i}')
    row = [F(0)] * nv; row[vs(k)] = 4; row[IAM] = -5; row[IQ1] = -1
    con(row, 0, 0, 'LZ')
    if k < nS:
        row = [F(0)] * nv; row[vs(k + 1)] = -4; row[IAM] = 5; row[IQ1] = 1
        con(row, -MG_, 0, 'HZ')
    # 权重
    w = {}
    w['danger'] = 4 * nS - 2
    w['j1>=t'] = 2 * (nS - 1)
    w['A1_1'] = 2
    w['squeeze'] = 2
    w['srt1'] = nS - 1
    w['B1_SS01'] = nS - 1
    w['B2_JJJ01'] = 2 * (nS - 1)
    w['A5_1'] = 2 * nS
    for i in range(2, nS):
        w[f'A5_{i}'] = 2
    cols = {}
    for nm, wt in w.items():
        idxs = [i for i, n in enumerate(names) if n == nm]
        assert len(idxs) == 1, (nm, idxs)
        cols[idxs[0]] = F(wt)
    acc = [F(0)] * nv
    bcy = F(0); bty = F(0)
    for i, wt in cols.items():
        for v in range(nv):
            acc[v] += wt * A[i][v]
        bcy += wt * bc[i]; bty += wt * bt[i]
    bad = [(v, c) for v, c in enumerate(acc) if c != 0]
    expect_bc = -F(1, 2) - 4 * (nS - 1) * MG_
    print(f'm={m}: nonzero cols: {bad if bad else "NONE"}; bc^Tw={bcy} (expect {expect_bc}) '
          f'{"OK" if bcy == expect_bc else "MISMATCH"}; bt^Tw={bty}')
