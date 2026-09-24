"""提取 firststep LP（口袋2角落，2件形态，q1_target=k）的 Farkas 证书。

方法（方案二）：原 LP min 0 s.t. Ax<=b infeasible
  <==> 对偶可行性 LP  A^T y = 0, b^T y = -1, y >= 0  可行。
此时 y 即 Farkas 证书：非零 y_i 对应约束的加权和给出 0 <= -1 的硬矛盾。
证书可把"LP 闭合"升级为符号证明原料。
"""
import numpy as np
from scipy.optimize import linprog
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pairing_feasible import bin_count_solutions

MARGIN = 1e-4


def build_all(m, cnt, t_fix, k=1):
    """构造 firststep LP（含 bounds 显式化为约束），返回 A, b, names, nv。"""
    a, b, c, d, e, f = cnt
    nS = m - 1
    nv = 2 + 2 * nS + 2
    ip, it = 0, 1
    def vs(i): return 2 + i
    def vj(i): return 2 + nS + i
    iam, iq1 = 2 + 2 * nS, 2 + 2 * nS + 1
    A, bb, names = [], [], []

    def con(row, rhs, nm):
        A.append(row); bb.append(rhs); names.append(nm)

    def zero():
        return [0.0] * nv

    # ---- 变量界显式化（bounds -> A x <= b）----
    r = zero(); r[ip] = 1.0;   con(r, 1.0, 'p<=1')
    r = zero(); r[ip] = -1.0;  con(r, 0.0, 'p>=0')
    r = zero(); r[it] = 1.0;   con(r, t_fix, 't<=tf')
    r = zero(); r[it] = -1.0;  con(r, -t_fix, 't>=tf')
    for i in range(nS):
        r = zero(); r[vs(i)] = -1.0; con(r, -(1 - 2 * t_fix + MARGIN), f's{i}>=1-2t')
        r = zero(); r[vs(i)] = 1.0;  con(r, 1.0, f's{i}<=1')
        r = zero(); r[vj(i)] = 1.0;  con(r, 2 * t_fix - MARGIN, f'j{i}<=2t')
    # ---- 结构约束（同 pairing_feasible.build_lp）----
    for i in range(nS):
        r = zero(); r[it] = 1.0; r[vj(i)] = -1.0; con(r, 0.0, f'j{i}>=t')
    r = zero(); r[ip] = -1.0; r[it] = -1.0; con(r, -1.25 - MARGIN, 'danger')
    for i in range(nS):
        r = zero(); r[ip] = 1.0; r[vs(i)] = -1.0; r[vj(i)] = -1.0; con(r, -MARGIN, f'pair{i}')
    for i in range(nS):
        for kk in range(nS):
            r = zero(); r[vj(i)] = 1.0; r[vs(kk)] = -1.0; con(r, 0.0, f'mon_j{i}_s{kk}')
    for kk in range(nS):
        r = zero(); r[it] = 1.0; r[vs(kk)] = -1.0; con(r, 0.0, f'mon_t_s{kk}')
    for i in range(nS):
        r = zero(); r[iam] = 1.0; r[vs(i)] = -1.0; con(r, 0.0, f'am<=s{i}')
        r = zero(); r[vj(i)] = 1.0; r[iq1] = -1.0; con(r, 0.0, f'j{i}<=q1')
    r = zero(); r[it] = 1.0; r[iq1] = -1.0; con(r, 0.0, 't<=q1')
    r = zero(); r[iq1] = 1.0; r[iam] = -1.0; con(r, 0.0, 'q1<=am')
    r = zero(); r[ip] = 1.0; r[iam] = -1.25; r[iq1] = -1.25; con(r, -MARGIN, 'p<K')
    r = zero(); r[iam] = 1.0; r[iq1] = 1.0; con(r, 1.0, 'L<=1')
    # firststep (q1_target=k)
    for i in range(nS - 1):
        r = zero(); r[vs(i)] = 1.0; r[vs(i + 1)] = -1.0; con(r, 0.0, f'srt{i}')
    for i in range(1, nS):
        r = zero(); r[vj(0)] = 1.0; r[vj(i)] = -1.0; con(r, 0.0, f'fs_j{i}')
    r = zero(); r[iq1] = 1.0; r[vj(0)] = -1.0; con(r, 0.0, 'q1<=j0')
    r = zero(); r[vs(k - 1)] = 4.0; r[iam] = -5.0; r[iq1] = -1.0; con(r, 0.0, 's0+q1<=K')
    for i in range(k - 1):
        r = zero(); r[vs(i)] = -4.0; r[iam] = 5.0; r[iq1] = 1.0; con(r, -MARGIN, f'fs_nofit{i}')
    # 装箱容量
    jslots = [vj(i) for i in range(nS)] + [it]
    def cap(idxs, nm):
        r = zero()
        for ix in idxs:
            r[ix] = 1.0
        con(r, 1.0, nm)
    for kk in range(a):
        cap([vs(2 * kk), vs(2 * kk + 1)], 'SS')
    for kk in range(b):
        cap([vs(2 * a + kk), jslots[kk]], 'SJ')
    jidx = b
    for kk in range(d):
        cap([jslots[jidx], jslots[jidx + 1], jslots[jidx + 2]], 'JJJ'); jidx += 3
    for kk in range(e):
        cap([jslots[jidx], jslots[jidx + 1]], 'JJ'); jidx += 2
    return np.array(A), np.array(bb), names, nv


def farkas(A, b):
    """解 A^T y = 0, b^T y = -1, y >= 0；feasible 返回 y，否则 None。"""
    ncon = A.shape[0]
    Aeq = np.vstack([A.T, b.reshape(1, -1)])
    beq = np.concatenate([np.zeros(A.shape[1]), [-1.0]])
    res = linprog(c=np.zeros(ncon), A_eq=Aeq, b_eq=beq,
                  bounds=(0, None), method='highs')
    return res.x if res.status == 0 else None


if __name__ == '__main__':
    m, t, k = 6, 0.32, 1
    cnts = bin_count_solutions(m)
    for cnt in cnts:
        A, b, names, nv = build_all(m, cnt, t, k)
        y = farkas(A, b)
        if y is None:
            print(f'箱型 {cnt}: 对偶可行 -> 角落存在（不应发生）')
            continue
        At_y = A.T @ y
        print(f'箱型 {cnt}: Farkas 证书已提取')
        print(f'  验证: ||A^T y||_inf = {np.abs(At_y).max():.2e}  (应≈0)')
        print(f'        b^T y = {b @ y:.4f}  (应=-1)')
        print(f'        min(y) = {y.min():.4f}  (应>=0)')
        nz = [(names[i], float(y[i])) for i in range(len(y)) if abs(y[i]) > 1e-6]
        print(f'  证书非零项（{len(nz)} 条，按权重降序）:')
        for nm, w in sorted(nz, key=lambda x: -x[1]):
            print(f'    [{nm:<12}]  w = {w:.4f}')
        break
