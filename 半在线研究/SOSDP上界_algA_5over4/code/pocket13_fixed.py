"""口袋1/3 修正编码 LP（firststep 同 farkas_fixed 修正：nofit 在 i>jj，fs 使 j_jj>=j_i）。
build_p1f: 口袋1子B（M0={x,y} 2件，他机2件含大任务）
build_p3f: 口袋3残留（M0={x,y,z} 3件，他机2件含大任务）
扫描：float 快扫 + 精确证书。
"""
from fractions import Fraction as F
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from farkas_fixed import float_cert, rationalize_verify, MG


def _build(m, k, nfix):
    nS = m - 1
    nv = nfix + 2 * nS + 2
    ix, iy = 0, 1
    iz = 2 if nfix == 3 else None
    off = nfix
    def vs(i): return off + i
    def vj(i): return off + nS + i
    iam, iq1 = off + 2 * nS, off + 2 * nS + 1
    A, bc, bt, names = [], [], [], []

    def con(row, c0, c1, nm):
        A.append([F(z) for z in row]); bc.append(F(c0)); bt.append(F(c1)); names.append(nm)

    def zero(): return [F(0)] * nv

    r = zero(); r[ix] = 1; r[iy] = -1; con(r, 0, 0, 'x<=y')
    if nfix == 3:
        r = zero(); r[iy] = 1; r[iz] = -1; con(r, 0, 0, 'y<=z')
    r = zero(); r[ix] = -1; con(r, 0, -1, 'x>=t')
    r = zero(); r[iy] = -1; con(r, -1 - MG, 2, 'y>=1-2t')
    r = zero(); r[iy] = 1; con(r, 1, 0, 'y<=1')
    r = zero()
    for v in [ix, iy] + ([iz] if nfix == 3 else []):
        r[v] = -1
    con(r, -F(5, 4), 1, 'danger')
    for i in range(nS):
        r = zero(); r[vs(i)] = -1; con(r, -1 - MG, 2, f's{i}>=1-2t')
        r = zero(); r[vs(i)] = 1;  con(r, 1, 0, f's{i}<=1')
        r = zero(); r[vj(i)] = 1;  con(r, -MG, 2, f'j{i}<=2t')
        r = zero(); r[vj(i)] = -1; con(r, 0, -1, f'j{i}>=t')
        r = zero()
        for v in [ix, iy] + ([iz] if nfix == 3 else []):
            r[v] = 1
        r[vs(i)] = -1; r[vj(i)] = -1
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
            r = zero(); r[vj(jj)] = -1; r[vj(i)] = 1; con(r, 0, 0, f'fs_j{i}')
    r = zero(); r[iq1] = 1; r[vj(jj)] = -1; con(r, 0, 0, f'q1<=j{jj}')
    r = zero(); r[vs(jj)] = 4; r[iam] = -5; r[iq1] = -1; con(r, 0, 0, 'sk+q1<=K')
    for i in range(jj + 1, nS):
        r = zero(); r[vs(i)] = -4; r[iam] = 5; r[iq1] = 1; con(r, -MG, 0, f'nofit{i}')
    r = zero()
    for v in [ix, iy] + ([iz] if nfix == 3 else []):
        r[v] = 1
    for i in range(nS):
        r[vs(i)] = 1; r[vj(i)] = 1
    con(r, m, -1, 'vol<=m')
    return A, bc, bt, names, nv


def build_p1f(m, k=1):
    return _build(m, k, 2)


def build_p3f(m, k=1):
    return _build(m, k, 3)


if __name__ == '__main__':
    for tag, build in [('口袋1子B', build_p1f), ('口袋3残留', build_p3f)]:
        print(f'==== {tag} 修正编码（m × k，float）====')
        for m in range(4, 13):
            row = []
            for k in range(1, m):
                A, bc, bt, names, nv = build(m, k)
                yf = float_cert(A, bc, bt)
                if yf is None:
                    row.append('FEAS')
                    continue
                y, N = rationalize_verify(A, bc, bt, yf)
                row.append('OK' if y is not None else 'RAT?')
            print(f'  m={m}: {row}')
