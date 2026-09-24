"""口袋2角落 3件形态(他机=senior+2 junior)的 firststep 闭合验证。

2件形态已证: best-fit第一步(q_1填最满能放下的senior机) + 机器对和s_i+j_i>p + danger
            ⟹ 角落 infeasible。
这里验证 3件形态(他机 senior+j1+j2, j1,j2∈[t,2t)) 是否同样闭合。
"""
import numpy as np
from scipy.optimize import linprog

MARGIN = 1e-4


def bin_cnt3(m):
    nS = m - 1
    nJ = 2 * (m - 1) + 1   # 2(m-1) 他机 junior + t
    out = []
    for a in range(nS // 2 + 1):
        for b in range(nS + 1):
            c = nS - 2 * a - b
            if c < 0:
                continue
            for d in range(nJ + 1):
                for e in range(nJ + 1):
                    f = a - d - e
                    if f < 0:
                        continue
                    if b + 3 * d + 2 * e + f != nJ:
                        continue
                    out.append((a, b, c, d, e, f))
    return out


def lp3(m, cnt, t_fix, kt, use_danger=True):
    a, b, c, d, e, f = cnt
    nS = m - 1
    nv = 2 + 3 * nS + 2
    ip, it = 0, 1
    def vs(i): return 2 + i
    def vj(i): return 2 + nS + i
    def vj2(i): return 2 + 2 * nS + i
    iam, iq1 = 2 + 3 * nS, 2 + 3 * nS + 1

    A, bb = [], []
    bounds = [(None, None)] * nv
    bounds[ip] = (0, 1)
    bounds[it] = (t_fix, t_fix)
    for i in range(nS):
        bounds[vs(i)] = (1 - 2 * t_fix + MARGIN, 1)
        bounds[vj(i)] = (None, 2 * t_fix - MARGIN)
        bounds[vj2(i)] = (None, 2 * t_fix - MARGIN)

    def row():
        r = [0.0] * nv; return r

    # junior 下界 j>=t, j2>=t
    for i in range(nS):
        r = row(); r[it] = 1; r[vj(i)] = -1; A.append(r); bb.append(0)
        r = row(); r[it] = 1; r[vj2(i)] = -1; A.append(r); bb.append(0)
    # danger
    if use_danger:
        r = row(); r[ip] = -1; r[it] = -1; A.append(r); bb.append(-1.25 - MARGIN)
    # 机器对和: s_i + j_i + j2_i >= p  ⟺ p - s - j - j2 <= -margin
    for i in range(nS):
        r = row(); r[ip] = 1; r[vs(i)] = -1; r[vj(i)] = -1; r[vj2(i)] = -1
        A.append(r); bb.append(-MARGIN)
    # 递减(单调): j_i,j2_i,t <= a_m <= s_i
    for i in range(nS):
        r = row(); r[vj(i)] = 1; r[iam] = -1; A.append(r); bb.append(0)
        r = row(); r[vj2(i)] = 1; r[iam] = -1; A.append(r); bb.append(0)
        r = row(); r[iam] = 1; r[vs(i)] = -1; A.append(r); bb.append(0)
    r = row(); r[it] = 1; r[iam] = -1; A.append(r); bb.append(0)
    # p<K: p <= 5(a_m+q_1)/4
    r = row(); r[ip] = 1; r[iam] = -1.25; r[iq1] = -1.25; A.append(r); bb.append(-MARGIN)
    # L<=1
    r = row(); r[iam] = 1; r[iq1] = 1; A.append(r); bb.append(1.0)

    # firststep: q_1 填第 kt 大 senior 机(索引 kt-1); q_1 = 该机较大 junior j_{kt-1}
    # senior 排序 s_0>=...>=s_{nS-1}
    for i in range(nS - 1):
        r = row(); r[vs(i)] = 1; r[vs(i + 1)] = -1; A.append(r); bb.append(0)
    jj = kt - 1
    # j_{jj} 是最大 junior(≥所有 j 和 j2), q_1=j_{jj}
    for i in range(nS):
        r = row(); r[vj(jj)] = 1; r[vj(i)] = -1; A.append(r); bb.append(0)
        r = row(); r[vj(jj)] = 1; r[vj2(i)] = -1; A.append(r); bb.append(0)
    r = row(); r[iq1] = 1; r[vj(jj)] = -1; A.append(r); bb.append(0)   # q1<=j_{jj}
    # 该机的第二 junior <= 第一 junior
    r = row(); r[vj2(jj)] = 1; r[vj(jj)] = -1; A.append(r); bb.append(0)
    # 前 kt-1 大 senior 放不下 q_1: -4s_i+5a_m+q_1<0
    for i in range(kt - 1):
        r = row(); r[vs(i)] = -4; r[iam] = 5; r[iq1] = 1; A.append(r); bb.append(-MARGIN)
    # 第 kt 大放得下: 4s_{kt-1}-5a_m-q_1<=0
    r = row(); r[vs(kt - 1)] = 4; r[iam] = -5; r[iq1] = -1; A.append(r); bb.append(0)

    # 装箱容量 (junior 池 = j_i + j2_i + t, 共 2nS+1)
    jslots = [vj(i) for i in range(nS)] + [vj2(i) for i in range(nS)] + [it]
    def cap(idxs):
        r = row()
        for ix in idxs:
            r[ix] = 1
        A.append(r); bb.append(1.0)
    for k in range(a):
        cap([vs(2 * k), vs(2 * k + 1)])
    for k in range(b):
        cap([vs(2 * a + k), jslots[k]])
    jidx = b
    for k in range(d):
        cap([jslots[jidx], jslots[jidx + 1], jslots[jidx + 2]]); jidx += 3
    for k in range(e):
        cap([jslots[jidx], jslots[jidx + 1]]); jidx += 2

    res = linprog(c=np.zeros(nv), A_ub=np.array(A), b_ub=np.array(bb), bounds=bounds, method="highs")
    return res.status


if __name__ == "__main__":
    import sys
    allclosed = True
    for m in [6, 7, 8, 9]:
        tl = (m - 1) / (4 * (m - 2))
        cnts = bin_cnt3(m)
        for t in np.linspace(tl + 0.005, 1 / 3, 4):
            feas_k = []
            for k in range(1, m):
                n = sum(lp3(m, c, t, k) == 0 for c in cnts)
                if n > 0:
                    feas_k.append(k)
            if feas_k:
                allclosed = False
                print(f"  m={m} t={t:.4f}: 3件形态可行! q_1填第{feas_k}大senior")
    print("结论:", "3件形态也全闭合" if allclosed else "3件形态有可行子情形(需进一步)")
