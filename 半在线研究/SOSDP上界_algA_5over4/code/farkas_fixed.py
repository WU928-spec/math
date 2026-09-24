"""口袋2角落（2件形态）修正编码的严格 LP 证书管线。

修正点（相对 farkas_constant.py 旧编码）：
  Algorithm A = best-fit 最满优先（toolbox.py:27）：q1 填放得下的【最大】senior 机
  - nofit 在较大 senior 侧（i>jj）：s_i+q1>K；旧编码误放 i<jj
  - fs 使 j_jj 为【最大】junior（=q1，j_jj>=j_i）；旧编码误为 j_jj<=j_i
  两条约束都是角落真实必要条件 ⟹ 修正编码是合法松弛（relaxation），infeasible ⟹ 角落空。
验证：精确 Fraction 证书（A^T y=0, bt^T y=0, bc^T y=-1, y>=0）+ 消融 + sanity。
"""
from fractions import Fraction as F
import numpy as np
from scipy.optimize import linprog
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pairing_feasible import bin_count_solutions

MG = F(1, 10000)


def build_fixed(m, cnt, k=1, use_nofit=True, use_fs=True, use_pair=True,
                use_danger=True, use_bins=True, use_kcap=True, use_mon=True):
    """修正版口袋2角落 LP。开关用于消融。t 只在右端 -> 常数证书覆盖全窗口。"""
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
    if use_danger:
        r = zero(); r[ip] = -1; r[it] = -1; con(r, -F(5, 4) - MG, 0, 'danger')
    if use_pair:
        for i in range(nS):
            r = zero(); r[ip] = 1; r[vs(i)] = -1; r[vj(i)] = -1; con(r, -MG, 0, f'pair{i}')
    if use_mon:
        for i in range(nS):
            for kk in range(nS):
                r = zero(); r[vj(i)] = 1; r[vs(kk)] = -1; con(r, 0, 0, f'mon_j{i}_s{kk}')
        for kk in range(nS):
            r = zero(); r[it] = 1; r[vs(kk)] = -1; con(r, 0, 0, f'mon_t_s{kk}')
    if use_kcap:
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
    if use_fs:
        for i in range(nS):
            if i != jj:
                r = zero(); r[vj(jj)] = -1; r[vj(i)] = 1; con(r, 0, 0, f'fs_j{i}')
        r = zero(); r[iq1] = 1; r[vj(jj)] = -1; con(r, 0, 0, f'q1<=j{jj}')
    r = zero(); r[vs(jj)] = 4; r[iam] = -5; r[iq1] = -1; con(r, 0, 0, 'sk+q1<=K')
    if use_nofit:
        for i in range(jj + 1, nS):
            r = zero(); r[vs(i)] = -4; r[iam] = 5; r[iq1] = 1; con(r, -MG, 0, f'nofit{i}')
    if use_bins:
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
    Af = np.array([[float(x) for x in row] for row in A])
    bcf = np.array([float(x) for x in bc]); btf = np.array([float(x) for x in bt])
    Aeq = np.vstack([Af.T, btf.reshape(1, -1), bcf.reshape(1, -1)])
    beq = np.concatenate([np.zeros(Af.shape[1]), [0.0, -1.0]])
    res = linprog(c=np.zeros(Af.shape[0]), A_eq=Aeq, b_eq=beq, bounds=(0, None), method='highs')
    return res.x if res.status == 0 else None


def rationalize_verify(A, bc, bt, yf):
    from fractions import Fraction
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
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'scan'
    if cmd == 'scan':
        print('修正编码：精确常数证书全扫（m × k，全称全 cnt）:')
        allok = True
        for m in range(4, 13):
            cnts = bin_count_solutions(m)
            row = []
            for k in range(1, m):
                okk = True
                for cnt in cnts:
                    A, bc, bt, names, nv = build_fixed(m, cnt, k)
                    yf = float_cert(A, bc, bt)
                    if yf is None:
                        okk = False; break
                    y, N = rationalize_verify(A, bc, bt, yf)
                    if y is None:
                        okk = False; break
                row.append('OK' if okk else 'X')
                if not okk: allok = False
            print(f'  m={m}: k=1..{m-1} -> [{" ".join(row)}]')
        print('结论:', '修正编码下全部 (m,k,cnt) 有精确常数证书 ✓' if allok else '有洞！')
    elif cmd == 'ablate':
        m, cnt, k = 6, (1, 3, 0, 1, 0, 0), 1
        base = build_fixed(m, cnt, k)
        print(f'消融（m={m} cnt={cnt} k={k}，基准: {"有证书" if float_cert(*base[:3]) is not None else "feasible"}）:')
        for nm, kw in [('去danger', dict(use_danger=False)), ('去pair', dict(use_pair=False)),
                       ('去mon递减', dict(use_mon=False)), ('去kcap组', dict(use_kcap=False)),
                       ('去fs', dict(use_fs=False)), ('去nofit', dict(use_nofit=False)),
                       ('去装箱', dict(use_bins=False))]:
            A, bc, bt, names, nv = build_fixed(m, cnt, k, **kw)
            print(f'   {nm:8s}: {"feasible（必要 ✓）" if float_cert(A, bc, bt) is None else "仍有证书（非必要!）"}')
    elif cmd == 'sanity':
        # 无 danger 的宽松配置必须 feasible（防假阴性）
        A, bc, bt, names, nv = build_fixed(6, (1, 3, 0, 1, 0, 0), 1, use_danger=False)
        print('sanity(去danger):', 'feasible ✓（LP 未把非角落判死）' if float_cert(A, bc, bt) is None else 'INFEASIBLE ✗ 假阴性风险!')
