"""a3_hi_analyze.py —— §3 hi 区子分析的数据底盘（agent-3，对口 main_beta_proof_draft §3 缺口）。

问题：k=2（low-zone 恰 2 台）且低端链存货 I>=2 的紧实例存活率与 hi 区匹配死法。
定义：I = #J 中 ≥ p−s₁+MG 的件数（引理 H 存货）；k = #{i : sᵢ ≤ K−q₁}（lowzone 台数，
1-based = jj+1）；K=5(s₁+q₁)/4。
分层（main 数据补正的双层机制）：
  L1 存货计数：k > I ⟹ mon2 升链死；
  L2 fs/q₁ 补杀：k ≤ I 但 fs 钉走 q₁ ⟹ 机 1 有效存货 I−1 < k 亦死；
  §3 残余：k=2 ∧ I>=2（低端链+fs 双过）⟹ hi 区（机 3..nS）窗口与残量 junior 匹配判定。
输出 (k, I) 联合分布 + §3 残余例数 + hi 匹配死因解剖。
"""
import numpy as np
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a3_tight_stress import build_tight_e0, build_tight_e1

MG = 1e-4


def analyze(m, e=0, nsamp=400, tgrid=(0.28, 0.30, 0.313, 0.32, 1 / 3), seed=11):
    rng = np.random.default_rng(seed + m * 10 + e)
    builder = build_tight_e0 if e == 0 else build_tight_e1
    joint = {}
    resid = []
    for t in tgrid:
        for _ in range(nsamp):
            got = builder(m, t, rng)
            if got is None:
                continue
            p, s, j = got
            nS = m - 1
            s1, q1 = s[0], j[-1]
            K = 5 * (s1 + q1) / 4
            I = sum(1 for x in j if x >= p - s1 + MG - 1e-12)
            k = sum(1 for x in s if x <= K - q1 + 1e-12)
            joint[(k, I)] = joint.get((k, I), 0) + 1
            # §3 残余：k=2 且低端链可排（I>=2 且 fs 后机1 有效存货 >=1）
            if k == 2 and I >= 2:
                resid.append((t, p, s, j))
    return joint, resid


def hi_verdict(t, p, s, j):
    """k=2 ∧ I>=2 实例：低端链安放（枚举 x₁∈存货\{q₁}）+ hi 区 DFS 匹配，判可行与否。"""
    nS = len(s)
    s1, q1 = s[0], j[-1]
    K = 5 * (s1 + q1) / 4
    highs = [x for x in j if x >= p - s1 + MG - 1e-12]
    for x1 in highs:
        if abs(x1 - q1) < 1e-12 and highs.count(q1) == 1:
            continue
        rest = [x for x in j if not (abs(x - x1) < 1e-12 and [x].pop() is None)]
        # 构造残量：j 去掉一件 x1 与 q1
        pool = list(j)
        pool.remove(x1)
        if q1 in pool:
            pool.remove(q1)
        else:
            continue
        # 机 2 pair + lowzone
        if not (s[1] + q1 >= p + MG - 1e-12 and s[1] <= K - q1 + 1e-12):
            continue
        # hi 区窗口匹配（机 3..nS，索引 2..nS-1）
        hims = list(range(2, nS))
        lo = {i: max(t, p - s[i] + MG) for i in hims}
        hi = {i: min(2 * t, K - s[i]) for i in hims}
        if any(lo[i] > hi[i] + 1e-12 for i in hims):
            return False, ('window', x1)
        pool.sort()
        hims_sorted = sorted(hims, key=lambda i: hi[i])
        used = [False] * len(pool)
        def dfs(idx):
            if idx == len(hims_sorted):
                return True
            i = hims_sorted[idx]
            for u, v in enumerate(pool):
                if not used[u] and lo[i] - 1e-12 <= v <= hi[i] + 1e-12:
                    used[u] = True
                    if dfs(idx + 1):
                        return True
                    used[u] = False
            return False
        if dfs(0):
            return True, ('HI-OK', x1)
    return False, ('all-x1-dead', None)


def main():
    import time
    t0 = time.time()
    for e in [0, 1]:
        alljoint = {}
        nres = 0
        nres_ok = 0
        for m in range(6, 15):
            joint, resid = analyze(m, e)
            for kk, vv in joint.items():
                alljoint[kk] = alljoint.get(kk, 0) + vv
            nres += len(resid)
            for t, p, s, j in resid[:60]:
                ok, info = hi_verdict(t, p, s, j)
                if ok:
                    nres_ok += 1
                    if nres_ok <= 3:
                        print(f'  ★ §3残余存活! e={e} m={m} t={t:.3f} x1={info}')
            print(f'e={e} m={m} 完成（{time.time()-t0:.0f}s，§3残余累计 {nres}）', flush=True)
        print(f'\ne={e} (k,I) 联合分布:')
        ks = sorted(set(k for k, _ in alljoint))
        Is = sorted(set(i for _, i in alljoint))
        hdr = '     I=' + ' '.join(f'{i:5d}' for i in Is)
        print(hdr)
        for k in ks:
            row = [alljoint.get((k, i), 0) for i in Is]
            print(f'  k={k:2d}: ' + ' '.join(f'{v:5d}' for v in row))
        print(f'e={e}: §3 残余（k=2∧I>=2）= {nres}，其中 hi 匹配可行 = {nres_ok}')


if __name__ == '__main__':
    main()
