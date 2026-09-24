"""main_reach_pack.py —— 方向 1 核心主张的全证据管线（主代理）。

主张（razor 带 (P) 的动力学闭合形式）：
  razor 带角落构型 + 动力学可达（best-fit 轨迹产生 fallback）⟹ 不可装箱（OPT>1）。
  若全称成立 ⟹ razor 带 (P) 闭合（无需装箱行/(W'')），与洞族"不可达"形成统一图景：
  洞族=不可达排除、razor 带=可达但不可装箱。

逐 razor 带 (m, cnt, k)：角落+mon2（无装箱行）采样可行点 → 实跑 Algorithm A（强制到达序）
→ 判可达性（fallback_event）→ 对可达点做精确装箱判定（DFS, cap-1 m 箱）。
表格：可达&可装箱 应恒为 0。
"""
import numpy as np
from scipy.optimize import linprog
import sys, os, itertools
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
    for t0 in [0.28, 0.30, 0.32, 1/3]:
        for _ in range(nsample):
            c = rng.standard_normal(nv)
            res = linprog(c=c, A_ub=np.vstack([A2, -np.eye(nv)[1]]),
                          b_ub=np.concatenate([bcf,[-t0]]), bounds=(None,None), method='highs')
            if res.status == 0: pts.append(res.x)
    return pts

def packs_into_m(items, m):
    items = sorted(items, reverse=True)
    bins = []
    def dfs(i):
        if i == len(items): return True
        seen = set()
        for b in range(len(bins)):
            kk = round(bins[b], 9)
            if kk in seen: continue
            if bins[b] + items[i] <= 1 + 1e-12:
                seen.add(kk); bins[b] += items[i]
                if dfs(i+1): return True
                bins[b] -= items[i]
        if len(bins) < m:
            bins.append(items[i])
            if dfs(i+1): return True
            bins.pop()
        return False
    return dfs(0)

def main(mlo=6, mhi=14, nsample=4):
    tot = reach = packable = reach_pack = 0
    for m in range(mlo, mhi+1):
        nS = m-1
        for cnt in [(1,m-3,0,1,0,0),(2,m-5,0,1,1,0)]:
            for k in range(2, m):
                pts = sample_points(m, cnt, k, nsample, seed=m*1000+k)
                for x in pts:
                    p, t = x[0], x[1]
                    s = list(x[2:2+nS]); j = list(x[2+nS:2+2*nS])
                    seq = sorted([p]+s, reverse=True) + sorted(j+[t], reverse=True)
                    ev = fallback_event(seq, m)
                    tot += 1
                    if ev is None: continue
                    reach += 1
                    items = [p]+s+j+[t]
                    if packs_into_m(items, m):
                        packable += 1
                        reach_pack += 1
                        print(f"  **可达且可装箱（=反例）** m={m} cnt={cnt} k={k} p={p:.3f} t={t:.3f}")
        print(f"m={m} 完成（累计 采样{tot} 可达{reach} 可达且可装箱{reach_pack}）")
    print(f"\n=== 判决 ===\nrazor 带采样 {tot}：可达 {reach}，可达且可装箱 {reach_pack}")
    print("reach_pack=0 ⟹ 主张成立（razor 带可达⟹不可装箱）⟹ (P) 动力学闭合")

if __name__ == '__main__':
    main()
