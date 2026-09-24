"""口袋2角落（firststep LP）的严格 LP 证书：精确有理数 + 覆盖连续 t 窗口。

关键：LP 里 t 只出现在右端（A 为 t 无关常数矩阵），故 b(t)=bc+t*bt。
常数证书 y（与 t 无关）存在  <=>  解  A^T y = 0, bt^T y = 0, bc^T y = -1, y >= 0。
若存在，则同一份 y 使  A^T y = 0, b(t)^T y = -1  对整个 t 窗口成立 -> 一个证书覆盖全部 t。
流程：浮点 LP 定位 -> Fraction 有理化 -> 精确验证（A^T y==0, bt^T y==0, bc^T y==-1, y>=0）。
"""
import numpy as np
from scipy.optimize import linprog
from fractions import Fraction
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pairing_feasible import bin_count_solutions

F = Fraction
MG = F(1, 10000)          # MARGIN = 1e-4（精确有理数）


def build_frac(m, cnt, k=1):
    """返回 A(Fraction 矩阵), bc(常数右端), bt(t 系数右端), names, nv。t 只出现在右端。
    firststep: q1 填第 k 大 senior 机（k=1..nS）。"""
    a, b, c, d, e, f = cnt
    nS = m - 1
    nv = 2 + 2 * nS + 2
    ip, it = 0, 1
    def vs(i): return 2 + i
    def vj(i): return 2 + nS + i
    iam, iq1 = 2 + 2 * nS, 2 + 2 * nS + 1
    A, bc, bt, names = [], [], [], []

    def con(row, c0, c1, nm):
        A.append([F(x) for x in row]); bc.append(F(c0)); bt.append(F(c1)); names.append(nm)

    def zero(): return [F(0)] * nv

    # ---- 变量界（右端含 t 的用 bt）----
    r = zero(); r[ip] = 1;   con(r, 1, 0, 'p<=1')
    r = zero(); r[ip] = -1;  con(r, 0, 0, 'p>=0')
    r = zero(); r[it] = 1;   con(r, 0, 1, 't<=tf')
    r = zero(); r[it] = -1;  con(r, 0, -1, 't>=tf')
    for i in range(nS):
        r = zero(); r[vs(i)] = -1; con(r, -1 - MG, 2, f's{i}>=1-2t')   # -(1-2t+MG)=-1+2t-MG
        r = zero(); r[vs(i)] = 1;  con(r, 1, 0, f's{i}<=1')
        r = zero(); r[vj(i)] = 1;  con(r, -MG, 2, f'j{i}<=2t')          # 2t-MG
    # ---- 结构约束 ----
    for i in range(nS):
        r = zero(); r[it] = 1; r[vj(i)] = -1; con(r, 0, 0, f'j{i}>=t')
    r = zero(); r[ip] = -1; r[it] = -1; con(r, -F(5, 4) - MG, 0, 'danger')
    for i in range(nS):
        r = zero(); r[ip] = 1; r[vs(i)] = -1; r[vj(i)] = -1; con(r, -MG, 0, f'pair{i}')
    for i in range(nS):
        for kk in range(nS):
            r = zero(); r[vj(i)] = 1; r[vs(kk)] = -1; con(r, 0, 0, f'mon_j{i}_s{kk}')
    for kk in range(nS):
        r = zero(); r[it] = 1; r[vs(kk)] = -1; con(r, 0, 0, f'mon_t_s{kk}')
    for i in range(nS):
        r = zero(); r[iam] = 1; r[vs(i)] = -1; con(r, 0, 0, f'am<=s{i}')
        r = zero(); r[vj(i)] = 1; r[iq1] = -1; con(r, 0, 0, f'j{i}<=q1')
    r = zero(); r[it] = 1; r[iq1] = -1; con(r, 0, 0, 't<=q1')
    r = zero(); r[iq1] = 1; r[iam] = -1; con(r, 0, 0, 'q1<=am')
    r = zero(); r[ip] = 1; r[iam] = -F(5, 4); r[iq1] = -F(5, 4); con(r, -MG, 0, 'p<K')
    r = zero(); r[iam] = 1; r[iq1] = 1; con(r, 1, 0, 'L<=1')
    # firststep (q1 填第 k 大 senior 机，索引 k-1)
    for i in range(nS - 1):
        r = zero(); r[vs(i)] = 1; r[vs(i + 1)] = -1; con(r, 0, 0, f'srt{i}')
    jj = k - 1
    for i in range(nS):
        if i != jj:
            r = zero(); r[vj(jj)] = 1; r[vj(i)] = -1; con(r, 0, 0, f'fs_j{i}')
    r = zero(); r[iq1] = 1; r[vj(jj)] = -1; con(r, 0, 0, f'q1<=j{jj}')
    r = zero(); r[vs(jj)] = 4; r[iam] = -5; r[iq1] = -1; con(r, 0, 0, 'sk+q1<=K')
    for i in range(k - 1):
        r = zero(); r[vs(i)] = -4; r[iam] = 5; r[iq1] = 1; con(r, -MG, 0, f'nofit{i}')
    # 装箱
    jslots = [vj(i) for i in range(nS)] + [it]
    def cap(idxs, nm):
        r = zero()
        for ix in idxs: r[ix] = 1
        con(r, 1, 0, nm)
    for kk in range(a): cap([vs(2 * kk), vs(2 * kk + 1)], 'SS')
    for kk in range(b): cap([vs(2 * a + kk), jslots[kk]], 'SJ')
    jidx = b
    for kk in range(d):
        cap([jslots[jidx], jslots[jidx + 1], jslots[jidx + 2]], 'JJJ'); jidx += 3
    for kk in range(e):
        cap([jslots[jidx], jslots[jidx + 1]], 'JJ'); jidx += 2
    return A, bc, bt, names, nv


def float_cert(A, bc, bt):
    """浮点解常数证书可行性 LP：A^T y=0, bt^T y=0, bc^T y=-1, y>=0。"""
    Af = np.array([[float(x) for x in row] for row in A])
    bcf = np.array([float(x) for x in bc])
    btf = np.array([float(x) for x in bt])
    ncon = Af.shape[0]
    Aeq = np.vstack([Af.T, btf.reshape(1, -1), bcf.reshape(1, -1)])
    beq = np.concatenate([np.zeros(Af.shape[1]), [0.0, -1.0]])
    res = linprog(c=np.zeros(ncon), A_eq=Aeq, b_eq=beq, bounds=(0, None), method='highs')
    return res.x if res.status == 0 else None


def rationalize_verify(A, bc, bt, yf):
    """把浮点 yf 有理化并精确验证。返回精确 y 或 None。"""
    for N in [10**3, 10**4, 10**5, 10**6, 10**7, 10**8]:
        y = [Fraction(float(v)).limit_denominator(N) for v in yf]
        ok = True
        # A^T y = 0 精确
        for j in range(len(A[0])):
            s = sum(A[i][j] * y[i] for i in range(len(y)))
            if s != 0: ok = False; break
        if not ok: continue
        # bt^T y = 0, bc^T y = -1 精确
        if sum(bt[i] * y[i] for i in range(len(y))) != 0: continue
        if sum(bc[i] * y[i] for i in range(len(y))) != -1: continue
        if any(v < 0 for v in y): continue
        return y, N
    return None, None


if __name__ == '__main__':
    print('口袋2角落（2件形态）精确常数证书扫描（m × k，每证书覆盖全 t 窗口）:')
    allok = True
    for m in range(4, 10):
        cnts = bin_count_solutions(m)
        ks = []
        for k in range(1, m):
            got = False
            for cnt in cnts:
                A, bc, bt, names, nv = build_frac(m, cnt, k)
                yf = float_cert(A, bc, bt)
                if yf is None:
                    continue
                y, N = rationalize_verify(A, bc, bt, yf)
                if y is not None:
                    got = True
                    break
            ks.append('OK' if got else 'X')
            if not got:
                allok = False
        print(f'  m={m}: k=1..{m-1} -> [{" ".join(ks)}]')
    print('结论:', '全部 (m,k) 有常数证书 ✓' if allok else '部分 (m,k) 需进一步处理')
