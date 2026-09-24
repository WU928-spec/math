"""快速 LP 管线（与 build_fixed/add_order 结果等价，大幅提速）：
优化1: 去冗余 mon 块（O(m^2)->O(m)，可行性不变——kcap 组 j<=q1<=am<=s 已蕴涵）。
优化2: h 强制 = nS-1-jj（不用枚举：i>jj nofit=hi 区，i<=jj fit+srt=low 区）。
优化3: 浮点构造+浮点求解；INFEASIBLE 时只对支撑行（非零 y 的行）重建 Fraction 精确验证。
"""
import numpy as np
from scipy.optimize import linprog
from fractions import Fraction as F
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

MGF = 1e-4
MG = F(1, 10000)


def rows_fixed(m, cnt, k, use_mon=False, use_order=True):
    """生成 (row(list[float]), bc(Fraction), bt(Fraction), name) 行列表。
    与 build_fixed + add_order(h=强制) 等价。row 系数均为二进制精确值(0,±1,±4,±5,±1.25)；
    bc/bt 用精确 Fraction（MG=1/10000），避免浮点 1e-4 有理化失真。"""
    a, b, c, d, e, f = cnt
    nS = m - 1
    nv = 2 + 2 * nS + 2
    ip, it = 0, 1
    def vs(i): return 2 + i
    def vj(i): return 2 + nS + i
    iam, iq1 = 2 + 2 * nS, 2 + 2 * nS + 1
    R = []

    def con(row, c0, c1, nm):
        R.append((row, F(c0) if not isinstance(c0, F) else c0, F(c1) if not isinstance(c1, F) else c1, nm))

    def zero(): return [0.0] * nv

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
    if use_mon:
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
    r = zero(); r[ip] = 1; r[iam] = -1.25; r[iq1] = -1.25; con(r, -MG, 0, 'p<K')
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
    if use_order:
        # 保序：h 强制 = nS-1-jj。low 区 0..jj（含 jj）：s<=K-q1 + junior 升序；hi 区 jj+1..nS-1：s>K-q1。
        for i in range(jj + 1):
            r = zero(); r[vs(i)] = 4; r[iam] = -5; r[iq1] = -1; con(r, 0, 0, f'lowzone{i}')
        for i in range(jj + 1, nS):
            r = zero(); r[vs(i)] = -4; r[iam] = 5; r[iq1] = 1; con(r, -MG, 0, f'hizone{i}')
        for i in range(jj):
            r = zero(); r[vj(i)] = 1; r[vj(i + 1)] = -1; con(r, 0, 0, f'ord{i}')
    return R, nv


def float_cert_rows(R, nv):
    Af = np.array([row for row, _, _, _ in R])
    bcf = np.array([float(c0) for _, c0, _, _ in R])
    btf = np.array([float(c1) for _, _, c1, _ in R])
    Aeq = np.vstack([Af.T, btf.reshape(1, -1), bcf.reshape(1, -1)])
    beq = np.concatenate([np.zeros(nv), [0.0, -1.0]])
    res = linprog(c=np.zeros(len(R)), A_eq=Aeq, b_eq=beq, bounds=(0, None), method='highs')
    return res.x if res.status == 0 else None


def exact_verify_support(R, nv, yf):
    """只对支撑行（yf 非零）验证 A^T y=0, bt^T y=0, bc^T y=-1。
    row 系数二进制精确（F(float) 无损），bc/bt 已是精确 Fraction。"""
    sup = [i for i in range(len(R)) if yf[i] > 1e-9]
    rows = [R[i] for i in sup]
    for N in [10**3, 10**4, 10**5, 10**6, 10**7]:
        y = [F(float(yf[i])).limit_denominator(N) for i in sup]
        ok = True
        for j in range(nv):
            s = sum(F(row[j]) * w for (row, _, _, _), w in zip(rows, y))
            if s != 0:
                ok = False; break
        if not ok: continue
        if sum(c1 * w for (_, _, c1, _), w in zip(rows, y)) != 0: continue
        if sum(c0 * w for (_, c0, _, _), w in zip(rows, y)) != -1: continue
        if any(w < 0 for w in y): continue
        return y, sup
    return None, None


if __name__ == '__main__':
    import time
    from pairing_feasible import bin_count_solutions
    from farkas_fixed import build_fixed, float_cert as old_fc
    from order_step import add_order

    print('=== 等价性验证 1：去 mon 块（feasibility 应一致）===')
    bad = 0
    for m in range(6, 13):
        for cnt in bin_count_solutions(m):
            for k in range(1, m):
                A, bc, bt, names, nv = build_fixed(m, cnt, k)
                old = old_fc(A, bc, bt) is not None
                R, nv2 = rows_fixed(m, cnt, k, use_order=False)
                new = float_cert_rows(R, nv2) is not None
                if old != new:
                    bad += 1
                    if bad < 4: print(f'  不一致 m={m} cnt={cnt} k={k}: 旧={old} 新={new}')
    print(f'  mon 块一致性: {"全一致 ✓" if bad == 0 else f"{bad} 处不一致"}')

    print('=== 等价性验证 2：h 强制=nS-1-jj vs 全 h 枚举 ===')
    bad = 0
    for m, cnt, k in [(12,(2,7,0,1,1,0),11),(15,(2,10,0,1,1,0),14),(18,(3,11,0,1,2,0),17),(18,(2,13,0,1,1,0),17),(20,(3,13,0,1,2,0),19)]:
        nS = m - 1
        enum_all = all(
            (lambda An: old_fc(An[0], An[1], An[2]) is not None)(
                add_order(*build_fixed(m, cnt, k)[:4], build_fixed(m, cnt, k)[4], nS, h))
            for h in range(nS + 1))
        R, nv2 = rows_fixed(m, cnt, k, use_order=True)
        forced = float_cert_rows(R, nv2) is not None
        tag = '一致' if enum_all == forced else '不一致!!'
        if enum_all != forced: bad += 1
        print(f'  m={m} cnt={cnt} k={k}: 全枚举={enum_all} 强制={forced}  {tag}')
    print(f'  h 强制一致性: {"全一致 ✓" if bad == 0 else f"{bad} 处不一致"}')

    print('=== 速度对比 ===')
    m = 18
    cnts = bin_count_solutions(m)
    t0 = time.time()
    for cnt in cnts:
        for k in range(1, m):
            A, bc, bt, names, nv = build_fixed(m, cnt, k)
            old_fc(A, bc, bt)
    t1 = time.time()
    for cnt in cnts:
        for k in range(1, m):
            R, nv2 = rows_fixed(m, cnt, k, use_order=True)
            yf = float_cert_rows(R, nv2)
            if yf is not None:
                exact_verify_support(R, nv2, yf)
    t2 = time.time()
    print(f'  旧管线 m={m} 全 cnt 全 k 浮点: {t1-t0:.1f}s')
    print(f'  新管线 m={m} 全 cnt 全 k 保序+精确化: {t2-t1:.1f}s')
