"""a1_b4_symbolic.py — B4_q 合法性 ∀m 符号证明的机械核验（a1_b4_symbolic.md  companion）。

四项核验：
 1. e=0：B4_q 行 == SJrev_{nS-q-1} 行（逐字节，恒等式）。
 2. e=1, q<=nS-4：B4_q 行 == SJrev_{nS-q-3} + jrt_{q+2} + jrt_{q+3} 行和。
 3. e=1 例外两格（q=nS-3, nS-2）：{S1v, srt, q1<=am, am<=s1, jmax<=q1, jrt} + B4破 不可行。
 4. 预言终验：角落（use_b4=False + sjrev + A5/LZ/HZ）+ B4破（无取等行） 全 t 网格不可行 ∀ uncond 配置。
反向对照（无 SJrev 时大片可行）见 a1_tight_real/a1_second_proof_review.md 的 F8 记录。
用法: python code/a1_b4_symbolic.py [--quick]
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from scipy.optimize import linprog
from fractions import Fraction as F
import a1_value_lp2 as V

MG_ = F(1, 10000)
TMESH = [0.27, 0.29, 0.30, 0.31, 0.32, 1 / 3]


def check_identities():
    ok = True
    for m in [6, 8, 11, 14]:
        nS = m - 1
        A, bc, bt, names, leg, nv = V.build(m, (1, m - 3, 0, 1, 0, 0), use_b4=True, use_sjrev=True)
        for q in range(3, nS - 1):
            i1, i2 = names.index(f'B4_q{q}'), names.index(f'SJrev_{nS - q - 1}')
            ok &= A[i1] == A[i2] and bc[i1] == bc[i2]
    print('[1] e=0: B4_q == SJrev_{nS-q-1} (m=6/8/11/14):', 'PASS' if ok else 'FAIL')
    ok2 = True
    for m in [10, 12, 14]:
        nS = m - 1
        A, bc, bt, names, leg, nv = V.build(m, (2, m - 5, 0, 1, 1, 0), use_b4=True, use_sjrev=True)
        for q in range(5, nS - 3):
            i_b4 = names.index(f'B4_q{q}')
            i_sj = names.index(f'SJrev_{nS - q - 3}')
            i1 = names.index(f'jrt{q + 2}'); i2 = names.index(f'jrt{q + 3}')
            comb = [A[i_sj][v] + A[i1][v] + A[i2][v] for v in range(nv)]
            ok2 &= comb == A[i_b4] and bc[i_sj] + bc[i1] + bc[i2] == bc[i_b4]
    print('[2] e=1, q<=nS-4: B4_q == SJrev + jrt + jrt (m=10/12/14):', 'PASS' if ok2 else 'FAIL')
    return ok and ok2


def check_exceptions():
    ok = True
    for m in range(8, 17):
        nS = m - 1
        A, bc, bt, names, leg, nv = V.build(m, (2, m - 5, 0, 1, 1, 0), use_b4=False, use_a1=False, use_a3=False)
        keep = [i for i, n in enumerate(names) if n.startswith(('S1v', 'srt', 'q1<=am', 'am<=s1', 'jmax<=q1', 'jrt'))]
        Af = np.array([[float(x) for x in A[i]] for i in keep])
        b = np.array([float(bc[i]) for i in keep]) + np.array([float(bt[i]) for i in keep]) * 0.3
        vs = lambda r: 3 + (r - 1); vj = lambda r: 3 + nS + (r - 1)
        for q in (nS - 3, nS - 2):
            if q < 5:
                continue
            row = [0.0] * nv; row[vs(nS + 1 - q)] = -1; row[vj(q + 2)] = -1
            res = linprog(c=np.zeros(nv), A_ub=np.vstack([Af, row]), b_ub=np.append(b, -1 - 1e-4),
                          bounds=(None, None), method='highs')
            ok &= res.status != 0
    print('[3] e=1 例外两格（q=nS-3, nS-2; m=8..16）+ B4破 不可行:', 'PASS' if ok else 'FAIL')
    return ok


def corner_rows(m, cnt, k):
    A, bc, bt, names, leg, nv = V.build(m, cnt, use_b4=False, use_sjrev=True)
    A, bc, bt = list(A), list(bc), list(bt)
    nS = m - 1
    IP, IAM, IQ1 = 0, 1, 2
    vs = lambda r: 3 + (r - 1); vj = lambda r: 3 + nS + (r - 1)
    def con(row, c0, c1):
        A.append([F(x) for x in row]); bc.append(F(c0)); bt.append(F(c1))
    for i in range(1, k + 1):
        row = [F(0)] * nv; row[IP] = 1; row[vs(i)] = -1; row[vj(nS - k + i)] = -1
        con(row, -MG_, 0)
    row = [F(0)] * nv; row[vs(k)] = 4; row[IAM] = -5; row[IQ1] = -1
    con(row, 0, 0)
    if k < nS:
        row = [F(0)] * nv; row[vs(k + 1)] = -4; row[IAM] = 5; row[IQ1] = 1
        con(row, -MG_, 0)
    return A, bc, bt, nv, vs, vj, nS


def check_final():
    n_all, bad = 0, []
    for m in range(6, 17):
        nS = m - 1
        for cnt in [(1, m - 3, 0, 1, 0, 0), (2, m - 5, 0, 1, 1, 0)]:
            a = cnt[0]
            for k in range(2, m - 2 * a - 1):
                q = nS - k
                if not (2 * a + 1 <= q <= nS - 2):
                    continue
                A, bc, bt, nv, vs, vj, _ = corner_rows(m, cnt, k)
                row = [F(0)] * nv; row[vj(q + 2)] = -1; row[vs(nS + 1 - q)] = -1
                A.append(row); bc.append(-1 - MG_); bt.append(F(0))
                Af = np.array([[float(x) for x in row] for row in A])
                bf = np.array([float(x) for x in bc]); btf = np.array([float(x) for x in bt])
                feas = [t0 for t0 in TMESH if t0 > float(F(m - 1, 4 * (m - 2)))
                        and linprog(c=np.zeros(nv), A_ub=Af, b_ub=bf + btf * t0,
                                    bounds=(None, None), method='highs').status == 0]
                n_all += 1
                if feas:
                    bad.append((m, cnt[0], k, q, feas))
    print(f'[4] B4破单飞（无取等行）全 t 网格：{n_all - len(bad)}/{n_all} 不可行',
          '' if not bad else f'FAIL {bad[:10]}')
    return not bad


if __name__ == '__main__':
    quick = '--quick' in sys.argv
    r = check_identities() & check_exceptions()
    r &= check_final() if not quick else True
    print('TOTAL:', 'PASS' if r else 'FAIL')
