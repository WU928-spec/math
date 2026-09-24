"""二步 LP：在修正编码上加 q_2（次大后续）的 best-fit 动态，试杀 m>=12 的 k≈m-1 洞。
q_2 = max{j_i : i≠jj}（他机 junior 之最大），角落 2 件形态下：
  (S1) q_2 >= j_i ∀i≠jj；q_2 <= q_1
  (S2) jj 机已 2 件，放不下 q_2：s_jj+q1+q_2 > K
  (S3) q_2 落 jj2=argmax{s_i : s_i+q_2<=K, i≠jj}：fit at jj2、nofit for i>jj2(i≠jj)、
       j_{jj2}=q_2（j_{jj2}>=j_i ∀i≠jj 且 q_2<=j_{jj2}）
每条都是角落必要条件（2 件形态 + best-fit 最满优先）。
"""
from fractions import Fraction as F
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from farkas_fixed import float_cert, rationalize_verify, MG
from pairing_feasible import bin_count_solutions


def build_fixed2(m, cnt, k=1, jj2=None):
    """build_fixed + 二步约束。jj2: q_2 落机索引（None 则只加 S1+S2）。"""
    a, b, c, d, e, f = cnt
    nS = m - 1
    nv = 2 + 2 * nS + 3          # 多一个 q_2 变量
    ip, it = 0, 1
    def vs(i): return 2 + i
    def vj(i): return 2 + nS + i
    iam, iq1, iq2 = 2 + 2 * nS, 2 + 2 * nS + 1, 2 + 2 * nS + 2
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

    # ---- 二步动态 ----
    # (S1) q_2 = max{j_i : i≠jj}（上界代理），q_2 <= q_1
    for i in range(nS):
        if i != jj:
            r = zero(); r[vj(i)] = 1; r[iq2] = -1; con(r, 0, 0, f'j{i}<=q2')
    r = zero(); r[iq2] = 1; r[iq1] = -1; con(r, 0, 0, 'q2<=q1')
    r = zero(); r[it] = 1; r[iq2] = -1; con(r, 0, 0, 't<=q2')   # q_2 是后续，>=t
    # (S2) jj 机已 2 件，放不下 q_2：s_jj+q1+q_2 > K ⟺ 4s_jj+4q1+4q2 > 5(a_m+q1)
    r = zero(); r[vs(jj)] = -4; r[iq1] = 1; r[iq2] = -4; r[iam] = 5
    con(r, -MG, 0, 'jj_nofit_q2')
    if jj2 is not None:
        # (S3) q_2 落 jj2：fit s_jj2+q_2<=K（K=(5/4)(a_m+q_1) 固定 cap，非 K2！）
        #   4s_jj2+4q_2 <= 5a_m+5q_1  ⟺  4s_jj2 - 5a_m - 5q_1 + 4q_2 <= 0
        r = zero(); r[vs(jj2)] = 4; r[iam] = -5; r[iq1] = -5; r[iq2] = 4; con(r, 0, 0, 's_jj2+q2<=K')
        # nofit: i>jj2, i≠jj（load s_i）放不下 q_2
        for i in range(jj2 + 1, nS):
            if i != jj:
                r = zero(); r[vs(i)] = -4; r[iam] = 5; r[iq2] = 1; con(r, -MG, 0, f'nofit2_{i}')
        # j_{jj2} = q_2：j_{jj2}>=j_i ∀i≠jj 且 q_2<=j_{jj2}
        for i in range(nS):
            if i != jj and i != jj2:
                r = zero(); r[vj(jj2)] = -1; r[vj(i)] = 1; con(r, 0, 0, f'fs2_j{i}')
        r = zero(); r[iq2] = 1; r[vj(jj2)] = -1; con(r, 0, 0, f'q2<=j{jj2}')
    return A, bc, bt, names, nv


if __name__ == '__main__':
    m, cnt, k = 12, (2, 7, 0, 1, 1, 0), 11
    nS = m - 1
    print('=== 二步 LP 杀洞测试 m=12 k=11 cnt=(2,7,0,1,1,0) ===')
    A, bc, bt, names, nv = build_fixed2(m, cnt, k, jj2=None)
    print(f'  仅 S1+S2（无 jj2）: {"feasible(洞在)" if float_cert(A, bc, bt) is None else "INFEASIBLE(洞灭)"}')
    jj = k - 1
    for j2 in range(nS):
        if j2 == jj:
            continue
        A, bc, bt, names, nv = build_fixed2(m, cnt, k, jj2=j2)
        st = 'feasible' if float_cert(A, bc, bt) is None else 'INFEASIBLE'
        print(f'  jj2={j2}: {st}')
