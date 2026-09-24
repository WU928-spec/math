"""main_reach_pack2.py —— 方向 1 主张证据管线 v2（优化版：先可达性筛，DFS 只喂可达点）。
主张：razor 带角落构型 + 动力学可达 ⟹ 不可装箱。
优化：轨迹可达性（便宜）先筛；装箱 DFS 只对可达点（体积剪枝+状态记忆化）。
"""
import numpy as np
from scipy.optimize import linprog
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hole_close import build_close
from toolbox import fallback_event

def sample_points(m, cnt, k, nsample, seed):
    A, bc, bt, names, nv = build_close(m, cnt, k)
    keep = [i for i, nm in enumerate(names) if nm not in ('SS','SJ','JJJ','JJ')]
    A = [A[i] for i in keep]; bc=[bc[i] for i in keep]; bt=[bt[i] for i in keep]
    Af = np.array([[float(x) for x in row] for row in A])
    bcf = np.array([float(x) for x in bc]); btf = np.array([float(x) for x in bt])
    A2 = Af.copy(); A2[:,1] -= btf
    rng = np.random.default_rng(seed)
    pts = []
    for t0 in [0.30, 0.32, 1/3]:
        for _ in range(nsample):
            c = rng.standard_normal(nv)
            res = linprog(c=c, A_ub=np.vstack([A2, -np.eye(nv)[1]]),
                          b_ub=np.concatenate([bcf,[-t0]]), bounds=(None,None), method='highs')
            if res.status == 0: pts.append(res.x)
    return pts

_memo = {}
def packs_into_m(items, m):
    items = tuple(sorted((round(v,6) for v in items), reverse=True))
    if items in _memo: return _memo[items]
    n = len(items); total = sum(items)
    if total > m: _memo[items]=False; return False
    bins = []
    def dfs(i, key):
        if i == n: return True
        if key in _memo: return _memo[key]
        v = items[i]
        if total - sum(items[:i]) > (m - sum(1 for _ in bins)) * 1.0 and False: pass
        seen = set()
        for b in range(len(bins)):
            kk = round(bins[b],6)
            if kk in seen: continue
            if bins[b] + v <= 1 + 1e-9:
                seen.add(kk); bins[b] += v
                if dfs(i+1, key + ((b, kk),)): return _memo.setdefault(key, True)
                bins[b] -= v
        if len(bins) < m:
            bins.append(v)
            if dfs(i+1, key + ((-1, v),)): return _memo.setdefault(key, True)
            bins.pop()
        _memo[key] = False
        return False
    r = dfs(0, (('s',),))
    _memo[items] = r
    return r

def main(mlo=6, mhi=14, nsample=3):
    tot = reach = reach_pack = 0
    for m in range(mlo, mhi+1):
        nS = m-1
        for cnt in [(1,m-3,0,1,0,0),(2,m-5,0,1,1,0)]:
            for k in [2, m//2, m-2, m-1]:
                for x in sample_points(m, cnt, k, nsample, seed=m*997+k):
                    p, t = x[0], x[1]
                    s = list(x[2:2+nS]); j = list(x[2+nS:2+2*nS])
                    seq = sorted([p]+s, reverse=True) + sorted(j+[t], reverse=True)
                    ev = fallback_event(seq, m)
                    tot += 1
                    if ev is None: continue
                    reach += 1
                    if packs_into_m([p]+s+j+[t], m):
                        reach_pack += 1
                        print(f"  **可达且可装箱** m={m} cnt={cnt} k={k} p={p:.3f} t={t:.3f}")
        print(f"m={m} 完成：采样{tot} 可达{reach} 可达且可装箱{reach_pack}")
    print(f"\n=== 判决 ===\nrazor 带采样 {tot}：可达 {reach}，可达且可装箱 {reach_pack}")

if __name__ == '__main__':
    main()
