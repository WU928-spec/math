"""裁决实验：firststep 编码是否符号反了？
对照：旧编码（nofit 在 i<jj 小senior侧, fs 使 j_jj<=j_i）
     新编码（nofit 在 i>jj 大senior侧, fs 使 j_jj>=j_i 即 j_jj=q1=最大junior）
Algorithm A = best-fit 最满优先（toolbox.py:27 loads[i]>loads[best]）：
q1 填放得下的最大 senior 机 ⟹ 更大 senior 机放不下（nofit 应在 i>jj）。
若旧编码 k>=2 自洽矛盾（3约束）而新编码 k>=2 feasible ⟹ 旧证书全是 artifact。
"""
from fractions import Fraction as F
import numpy as np
from scipy.optimize import linprog
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from farkas_constant import build_frac, float_cert, MG
from pairing_feasible import bin_count_solutions


def build_fixed(m, cnt, k=1):
    """修正版口袋2角落 LP：nofit 在 i>jj，fs 使 j_jj>=j_i。其余同 build_frac。"""
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

    r = zero(); r[ip] = 1;   con(r, 1, 0, 'p<=1')
    r = zero(); r[ip] = -1;  con(r, 0, 0, 'p>=0')
    r = zero(); r[it] = 1;   con(r, 0, 1, 't<=tf')
    r = zero(); r[it] = -1;  con(r, 0, -1, 't>=tf')
    for i in range(nS):
        r = zero(); r[vs(i)] = -1; con(r, -1 - MG, 2, f's{i}>=1-2t')
        r = zero(); r[vs(i)] = 1;  con(r, 1, 0, f's{i}<=1')
        r = zero(); r[vj(i)] = 1;  con(r, -MG, 2, f'j{i}<=2t')
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
    for i in range(nS - 1):
        r = zero(); r[vs(i)] = 1; r[vs(i + 1)] = -1; con(r, 0, 0, f'srt{i}')
    jj = k - 1
    for i in range(nS):
        if i != jj:
            # 修正：j_jj 是最大 junior（=q1）：j_jj >= j_i
            r = zero(); r[vj(jj)] = -1; r[vj(i)] = 1; con(r, 0, 0, f'fs_j{i}')
    r = zero(); r[iq1] = 1; r[vj(jj)] = -1; con(r, 0, 0, f'q1<=j{jj}')
    r = zero(); r[vs(jj)] = 4; r[iam] = -5; r[iq1] = -1; con(r, 0, 0, 'sk+q1<=K')
    # 修正：nofit 在较大 senior 侧 i>jj
    for i in range(jj + 1, nS):
        r = zero(); r[vs(i)] = -4; r[iam] = 5; r[iq1] = 1; con(r, -MG, 0, f'nofit{i}')
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


if __name__ == '__main__':
    m, cnt = 6, (1, 3, 0, 1, 0, 0)
    print('=== m=6 cnt=(1,3,0,1,0,0) 对照 ===')
    for k in [1, 2, 3]:
        Ao, bco, bto, no, nvo = build_frac(m, cnt, k)
        old = 'feasible' if float_cert(Ao, bco, bto) is None else 'INFEASIBLE(有证书)'
        An, bcn, btn, nn, nvn = build_fixed(m, cnt, k)
        new = 'feasible' if float_cert(An, bcn, btn) is None else 'INFEASIBLE(有证书)'
        print(f'  k={k}: 旧编码 {old:18s} | 新编码 {new}')
    print()
    print('=== 新编码全扫 (m=5..8 全 cnt 全 k)：feasible 计数 ===')
    for mm in range(5, 9):
        cnts = bin_count_solutions(mm)
        for k in range(1, mm):
            nf = 0
            for cn in cnts:
                An, bcn, btn, nn, nvn = build_fixed(mm, cn, k)
                if float_cert(An, bcn, btn) is None:
                    nf += 1
            print(f'  m={mm} k={k}: {nf}/{len(cnts)} feasible')
