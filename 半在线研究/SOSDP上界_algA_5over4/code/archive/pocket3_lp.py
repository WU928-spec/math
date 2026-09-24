"""口袋3残留（最闲机M0恰3件{x,y,z}，他机2件台含大任务）LP + 精确常数证书。
结构同 pocket1_lp：t 只在右端 -> 常数证书覆盖全 t 窗口。
"""
import numpy as np
from scipy.optimize import linprog
from fractions import Fraction
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

F = Fraction
MG = F(1, 10000)


def build_p3(m, k=1):
    nS = m - 1
    nv = 3 + 2 * nS + 2
    ix, iy, iz = 0, 1, 2
    def vs(i): return 3 + i
    def vj(i): return 3 + nS + i
    iam, iq1 = 3 + 2 * nS, 3 + 2 * nS + 1
    A, bc, bt, names = [], [], [], []

    def con(row, c0, c1, nm):
        A.append([F(z) for z in row]); bc.append(F(c0)); bt.append(F(c1)); names.append(nm)

    def zero(): return [F(0)] * nv

    r = zero(); r[ix] = 1; r[iy] = -1; con(r, 0, 0, 'x<=y')
    r = zero(); r[iy] = 1; r[iz] = -1; con(r, 0, 0, 'y<=z')
    r = zero(); r[ix] = -1; con(r, 0, -1, 'x>=t')
    r = zero(); r[ix] = -1; r[iy] = -1; r[iz] = -1; con(r, -F(5, 4), 1, 'danger')
    for i in range(nS):
        r = zero(); r[vs(i)] = -1; con(r, -1 - MG, 2, f's{i}>=1-2t')
        r = zero(); r[vs(i)] = 1; con(r, 1, 0, f's{i}<=1')
        r = zero(); r[vj(i)] = 1; con(r, -MG, 2, f'j{i}<=2t')
        r = zero(); r[vj(i)] = -1; con(r, 0, -1, f'j{i}>=t')
        r = zero(); r[ix] = 1; r[iy] = 1; r[iz] = 1; r[vs(i)] = -1; r[vj(i)] = -1
        con(r, -MG, 0, f'mach{i}>M0')
        r = zero(); r[vj(i)] = 1; r[iam] = -1; con(r, 0, 0, f'j{i}<=am')
        r = zero(); r[iam] = 1; r[vs(i)] = -1; con(r, 0, 0, f'am<=s{i}')
        r = zero(); r[vj(i)] = 1; r[iq1] = -1; con(r, 0, 0, f'j{i}<=q1')
    r = zero(); r[iam] = -1; con(r, 0, -1, 't<=am')
    r = zero(); r[iam] = 1; r[iq1] = 1; con(r, 1, 0, 'L<=1')
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
    # 体积（简化装箱）
    r = zero(); r[ix] = 1; r[iy] = 1; r[iz] = 1
    for i in range(nS):
        r[vs(i)] = 1; r[vj(i)] = 1
    con(r, m, -1, 'vol<=m')
    return A, bc, bt, names, nv


def float_cert(A, bc, bt):
    Af = np.array([[float(x) for x in row] for row in A])
    bcf = np.array([float(x) for x in bc]); btf = np.array([float(x) for x in bt])
    Aeq = np.vstack([Af.T, btf.reshape(1, -1), bcf.reshape(1, -1)])
    beq = np.concatenate([np.zeros(Af.shape[1]), [0.0, -1.0]])
    res = linprog(c=np.zeros(Af.shape[0]), A_eq=Aeq, b_eq=beq, bounds=(0, None), method='highs')
    return res.x if res.status == 0 else None


def rationalize_verify(A, bc, bt, yf):
    for N in [10**3, 10**4, 10**5, 10**6, 10**7]:
        y = [Fraction(float(v)).limit_denominator(N) for v in yf]
        ok = True
        for j in range(len(A[0])):
            if sum(A[i][j] * y[i] for i in range(len(y))) != 0:
                ok = False; break
        if not ok: continue
        if sum(bt[i] * y[i] for i in range(len(y))) != 0: continue
        if sum(bc[i] * y[i] for i in range(len(y))) != -1: continue
        if any(v < 0 for v in y): continue
        return y, N
    return None, None


if __name__ == '__main__':
    print('口袋3残留（M0=3件，他机2件台含大任务）常数证书扫描（m × k）:')
    for m in range(4, 9):
        row = []
        for k in range(1, m):
            A, bc, bt, names, nv = build_p3(m, k)
            yf = float_cert(A, bc, bt)
            if yf is None:
                row.append('feas')
                continue
            y, N = rationalize_verify(A, bc, bt, yf)
            row.append('OK' if y is not None else '?')
        print(f'  m={m}: k=1..{m-1} -> {row}')
