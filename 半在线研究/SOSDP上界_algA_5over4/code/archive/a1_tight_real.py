"""a1_tight_real.py — σ>0 可装箱见证的"真角落"分类器（mon2/fs/LZ-HZ 可实现性）。

承接 a1_tight_test.py 的发现：值语言角落+sliver+可装箱+σ>0 见证存在。
本脚本对每个见证判定是否存在合法 k（LZ/HZ 值确定）与单调配对指派：
  seniors 升序 s_1..s_nS；k=#{s_i<=K-q1}；低端区 i<=k 须 j 不减（mon2）且机 k 取 q1=j_nS(fs)；
  pair: s_i+j>=p+MG；cap: s_i+j<=K。hi 区任意双射。
分类：real_thin（k<=nS-2 可实现=真角落反例⟹BREAKING）/ real_knS（仅 k=nS）/ ghost（不可实现）。
"""
import numpy as np, sys, os, json, time
from fractions import Fraction as F
from scipy.optimize import linprog
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a1_value_lp2 as V
from a2_g1_flow import typed_feasible
from farkas_fixed import MG

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'a1_tight_real.jsonl')
PMG = 1e-4


def realizable(s, j, p, q1, K):
    """返回 (可达性, k)：k 由值唯一确定 #{s<=K-q1}；DFS 单调指派。"""
    nS = len(s)
    k = len([i for i in range(nS) if s[i] <= K - q1 + 1e-9])
    if k == 0 or k > nS:
        return False, k
    jmax = j[-1]
    used = [False] * nS

    def dfs(i, prev_j):
        if i == nS:
            return True
        lo = prev_j if i < k else 0
        for jj in range(lo, nS):
            if used[jj]:
                continue
            if i == k - 1 and j[jj] != jmax:
                continue  # fs
            sm = s[i] + j[jj]
            if sm < p + PMG - 1e-9:
                continue
            if sm > K + 1e-9:
                continue
            used[jj] = True
            if dfs(i + 1, jj):
                return True
            used[jj] = False
        return False

    return dfs(0, 0), k


def build_lp(m, cnt, t0, sigma_lb=None):
    A, bc, bt, names, leg, nv = V.build(m, cnt, use_a2=False, use_b4=False, use_sjrev=False)
    nS = m - 1
    IP = 0
    vs = lambda r: 3 + (r - 1)
    vj = lambda r: 3 + nS + (r - 1)

    def con(row, c0, c1, nm):
        A.append([F(x) for x in row]); bc.append(F(c0)); bt.append(F(c1)); names.append(nm)

    z = [F(0)] * nv
    r_ = list(z); r_[vj(1)] = -1; r_[vj(2)] = -1; r_[vj(3)] = -1
    con(r_, -1 - MG, 0, 'sliver_j1j2j3')
    for rr in range(1, nS + 1):
        r_ = list(z); r_[IP] = 1; r_[vs(nS + 1 - rr)] = -1; r_[vj(rr)] = -1
        con(r_, -MG, 0, f'A1M_{rr}')
    r_ = list(z); r_[IP] = -1
    con(r_, -F(5, 4) - MG, 1, 'dangerM')
    if sigma_lb is not None:
        r_ = list(z)
        for rr in range(1, nS + 1):
            r_[vs(rr)] = 1; r_[vj(rr)] = 1
        con(r_, nS - float(sigma_lb), -1, 'sigma_lb')
    Af = np.array([[float(x) for x in row] for row in A])
    b = np.array([float(x) for x in bc]) + np.array([float(x) for x in bt]) * t0
    return Af, b, nv, vs, vj, nS


def main():
    tmesh = [0.27, 0.30, 0.31, 0.32, 0.3333, 1 / 3]
    t_start = time.time()
    stat = {'configs': 0, 'tested': 0, 'packable': 0, 'real_thin': 0, 'real_knS': 0, 'ghost': 0}
    witnesses = []
    for m in range(6, 11):
        nS = m - 1
        for cnt in [(1, m - 3, 0, 1, 0, 0), (2, m - 5, 0, 1, 1, 0)]:
            for t0 in tmesh:
                if t0 <= float(F(m - 1, 4 * (m - 2))):
                    continue
                stat['configs'] += 1
                Af, b, nv, vs, vj, nS_ = build_lp(m, cnt, t0)
                cmin = np.zeros(nv)
                for rr in range(1, nS + 1):
                    cmin[vs(rr)] = 1; cmin[vj(rr)] = 1
                res = linprog(c=cmin, A_ub=Af, b_ub=b, bounds=(None, None), method='highs')
                if not res.success:
                    continue
                sig_max = (nS - t0) - res.fun
                if sig_max <= 1e-6:
                    continue
                Af2, b2, nv, vs, vj, nS_ = build_lp(m, cnt, t0, sigma_lb=sig_max * 0.5)
                for it in range(80):
                    rng = np.random.default_rng(7919 * m + 101 * cnt[0] + it)
                    rs = linprog(c=rng.normal(size=nv), A_ub=Af2, b_ub=b2,
                                 bounds=(None, None), method='highs')
                    if not rs.success:
                        continue
                    x = rs.x
                    s = [x[vs(r)] for r in range(1, nS + 1)]
                    j = [x[vj(r)] for r in range(1, nS + 1)]
                    sig = (nS - t0) - (sum(s) + sum(j))
                    if sig <= 1e-6:
                        continue
                    stat['tested'] += 1
                    if not typed_feasible(list(s), list(j) + [t0], cnt):
                        continue
                    stat['packable'] += 1
                    p_v, am_v, q1_v = x[0], x[1], x[2]
                    K_v = 1.25 * (am_v + q1_v)
                    ok, k = realizable(list(s), list(j), p_v, q1_v, K_v)
                    cls = ('real_thin' if (ok and k <= nS - 2) else
                           'real_knS' if ok else 'ghost')
                    stat[cls] += 1
                    if cls == 'real_thin':
                        witnesses.append({'m': m, 'cnt': cnt[0], 't': t0, 'sigma': sig, 'k': k,
                                          'p': round(p_v, 6), 'K': round(K_v, 6),
                                          's': [round(v, 6) for v in s],
                                          'j': [round(v, 6) for v in j]})
                    with open(OUT, 'a') as f:
                        f.write(json.dumps({'m': m, 'cnt': cnt[0], 't': round(t0, 6),
                                            'sigma': round(sig, 6), 'class': cls, 'k': k}) + '\n')
                    break
                if time.time() - t_start > 420:
                    print('[timeout]', stat, flush=True)
                    return
    print('[done]', stat)
    if witnesses:
        print('[BREAKING] 真角落（含薄层 k<=nS-2）σ>0 可装箱反例：')
        for w in witnesses[:3]:
            print(json.dumps(w))
    else:
        print('[ok] 无 real_thin 见证：值级 σ>0 见证全部仅 k=nS 可实现或 ghost')


if __name__ == '__main__':
    main()
