"""XTRI 行合法性证伪器 v2（agent-4）：限定 razor 窗口真角落。

XTRI: t+j₀+j₁≤1（j₀,j₁=标号后最小两台 senior 机的 junior）。
真角落 = 角落形状事件（检测同 fuzz_mon2）+ OPT≤1（精确装箱）+ t≤1/3 + p+t>5/4。
(B) 反例 = 真角落中 t+j₀+j₁>1 ⟹ XTRI 非法（路线级假阳性，立即上板）。
(A) 反例 = 真角落中 hi 区 junior < j₁ ⟹ "j₀,j₁=全局最小两件"不成立
    （不直接杀 XTRI，但杀"最小三元组"索引论证——供供给引理定位）。

用法: python a4_fuzz_tri2.py [budget_sec]
"""
import numpy as np
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fuzz_mon2 import track_run

STATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fuzz_tri2_state.json')


def packs_exact(items, m, cap=1.0):
    items = sorted(items, reverse=True)
    if items[0] > cap + 1e-9:
        return False
    loads = [0.0] * m

    def dfs(i):
        if i == len(items):
            return True
        w = items[i]
        seen = set()
        for b in range(len(loads)):
            if loads[b] in seen or loads[b] + w > cap + 1e-9:
                continue
            seen.add(loads[b])
            loads[b] += w
            if dfs(i + 1):
                return True
            loads[b] -= w
            if loads[b] < 1e-9:
                break
        return False
    return dfs(0)


def check_tri2(jobs, m):
    if len(jobs) != 2 * m:
        return None
    t = jobs[-1]
    if t > 1 / 3 + 1e-12:
        return None
    p = jobs[0]
    if p + t <= 1.25 + 1e-9:
        return None
    if not packs_exact(jobs, m):
        return None
    loads, mach, fb_idx, L = track_run(jobs, m)
    if fb_idx != len(jobs) - 1:
        return None
    K = 1.25 * L
    mi = max(range(m), key=lambda i: loads[i])
    if len(mach[mi]) != 2 or mach[mi][0] != jobs[0]:
        return None
    if any(len(mm) != 2 for mm in mach):
        return None
    others = [mm for i, mm in enumerate(mach) if i != mi]
    q1 = jobs[m]
    loads2 = [0.0] * m
    mach2 = [[] for _ in range(m)]
    for j, pp in enumerate(jobs[:m]):
        loads2[j] += pp; mach2[j].append(pp)
    best = -1
    for i in range(m):
        if loads2[i] + q1 <= K + 1e-12 and (best < 0 or loads2[i] > loads2[best]):
            best = i
    if best < 0:
        return None
    s_star = mach2[best][0]
    srt = sorted(others, key=lambda mm: (mm[0], mm[1]))
    jj = max(i for i, mm in enumerate(srt) if mm[0] <= s_star + 1e-9)
    if abs(srt[jj][0] - s_star) > 1e-9 or abs(srt[jj][1] - q1) > 1e-9:
        return None
    j0, j1 = srt[0][1], srt[1][1]
    hi = [mm[1] for mm in srt[jj + 1:]]
    tri = t + j0 + j1
    out = {'tri': tri, 'j0': j0, 'j1': j1, 't': t, 'p': p}
    if hi:
        out['hi_min'] = min(hi)
        out['hi_lt_j1'] = sum(1 for x in hi if x < j1 - 1e-9)
    else:
        out['hi_min'] = None; out['hi_lt_j1'] = 0
    return out


def main():
    t0 = time.time()
    budget = float(sys.argv[1]) if len(sys.argv) > 1 else 240.0
    start_n = 0
    stats = {'tested': 0, 'corner': 0, 'violB': 0, 'violA': 0}
    if os.path.exists(STATE):
        with open(STATE) as f:
            st = json.load(f)
        start_n = st.get('tested', 0)
        stats = st.get('stats', stats)
    rng = np.random.default_rng(20260923)
    n = start_n
    tris = []
    while time.time() - t0 < budget:
        n += 1
        m = int(rng.integers(4, 13))
        njobs = 2 * m
        u = rng.random()
        if u < 0.4:
            vals = rng.uniform(0.25, 1.0, njobs)
        elif u < 0.8:
            levels = np.array([1 / 3, 5 / 12, 1 / 2, 7 / 12, 2 / 3, 3 / 4, 11 / 12, 1.0])
            vals = rng.choice(levels, njobs) + rng.uniform(-0.01, 0.01, njobs)
            vals = np.clip(vals, 0.05, 1.0)
        else:
            # razor 偏好：大头 p≈0.9、小 t≤1/3、senior 窄带
            vals = np.concatenate([rng.uniform(0.85, 1.0, 1),
                                   rng.uniform(0.45, 0.72, m - 1),
                                   rng.uniform(0.30, 0.45, m - 1),
                                   rng.uniform(0.26, 1 / 3, 1)])
        jobs = sorted(vals.tolist(), reverse=True)
        stats['tested'] += 1
        r = check_tri2(jobs, m)
        if r is None:
            continue
        stats['corner'] += 1
        tris.append(r['tri'])
        if r['tri'] > 1 + 1e-9:
            stats['violB'] += 1
            print(f'  ✗✗ B反例(XTRI非法!): tri={r["tri"]:.4f} m={m} t={r["t"]:.4f} p={r["p"]:.4f}\n'
                  f'     jobs={np.round(jobs,4).tolist()}', flush=True)
        if r['hi_lt_j1'] > 0:
            stats['violA'] += 1
            if stats['violA'] <= 5:
                print(f'  ✗ A反例(j0,j1非全局最小): hi_min={r["hi_min"]:.4f} < j1={r["j1"]:.4f}, '
                      f'tri={r["tri"]:.4f}（仍{"≤1 ✓" if r["tri"]<=1 else ">1!"}）', flush=True)
        if n % 20000 == 0:
            ta = np.array(tris) if tris else np.array([0.0])
            print(f'  ... {n} ({time.time()-t0:.0f}s) 真角落 {stats["corner"]} '
                  f'B反例 {stats["violB"]} A反例 {stats["violA"]} tri_max={ta.max():.4f}', flush=True)
            with open(STATE, 'w') as f:
                json.dump({'tested': n, 'stats': stats}, f)
    ta = np.array(tris) if tris else np.array([0.0])
    with open(STATE, 'w') as f:
        json.dump({'tested': n, 'stats': stats}, f)
    print(f'完成: 总测 {stats["tested"]} razor真角落 {stats["corner"]} '
          f'B反例(XTRI非法) {stats["violB"]} A反例(索引非最小) {stats["violA"]}')
    print(f't+j0+j1: max={ta.max():.4f} p99={np.percentile(ta,99) if len(ta)>10 else 0:.4f}')
    print('结论:', 'XTRI 行在 razor 真角落实证成立 ✓' if stats['violB'] == 0 and stats['corner'] > 0
          else ('未采到真角落（需加样）' if stats['corner'] == 0 else 'XTRI 非法——闭合为假阳性!'))


if __name__ == '__main__':
    main()
