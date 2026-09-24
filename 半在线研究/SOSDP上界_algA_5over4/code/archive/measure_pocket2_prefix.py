"""口袋 2 前缀比值定向测量 v2（合规版）。

预估耗时: 12 万例纯模拟 ~2 分钟；opt_float 仅在 n<=16 的前缀上调用（守卫）。
输出: 前缀比值 > 1.15 的真口袋 2 事件 top 榜。
"""
import json, random, time

def trace(jobs, m):
    loads = [0.0]*m; cnt = [0]*m; fbs = []; L = None
    for j, p in enumerate(jobs):
        if j < m:
            loads[j] += p; cnt[j] += 1
        else:
            if j == m: L = jobs[m-1]+jobs[m]
            cap = 1.25*L
            best = -1
            for i in range(m):
                if loads[i]+p <= cap+1e-12 and (best < 0 or loads[i] > loads[best]):
                    best = i
            if best >= 0:
                loads[best] += p; cnt[best] += 1
            else:
                mn = min(range(m), key=lambda i: loads[i])
                fbs.append((j, p, cnt[mn], loads[mn]))
                loads[mn] += p; cnt[mn] += 1
    return max(loads), fbs

def opt_float(jobs, m):
    from functools import lru_cache
    n = len(jobs)
    tot = sum(jobs)
    subsum = [0.0]*(1 << n)
    for mask in range(1, 1 << n):
        lsb = mask & (-mask)
        subsum[mask] = subsum[mask ^ lsb] + jobs[lsb.bit_length()-1]
    def can(cap):
        @lru_cache(maxsize=None)
        def dfs(mask, k):
            if mask == 0: return True
            if k == 0: return False
            if subsum[mask] > k*cap + 1e-9: return False
            sub = mask
            while sub:
                if subsum[sub] <= cap + 1e-9 and dfs(mask ^ sub, k-1):
                    return True
                sub = (sub-1) & mask
            return False
        return dfs((1 << n)-1, m)
    lo, hi = max(tot/m, max(jobs)), tot
    for _ in range(40):
        mid = (lo+hi)/2
        if can(mid): hi = mid
        else: lo = mid
    return hi

def main(N=120000, seed=3):
    random.seed(seed)
    hits = []
    t0 = time.time()
    skipped = 0
    for it in range(N):
        m = random.choice((5, 6, 7, 8))
        n = random.randint(m+1, 3*m-1)
        mode = random.random()
        if mode < 0.5:
            jobs = sorted([random.randint(1, 12) for _ in range(n)], reverse=True)
        else:
            pi = random.randint(8, 12)
            jobs = sorted([pi] + [random.randint(4, 9) for _ in range(n-1)], reverse=True)
        ca, fbs = trace(jobs, m)
        if not fbs:
            continue
        jidx, p, c, l = fbs[-1]
        if c != 1:
            continue
        if jidx + 1 > 16:      # 复杂度守卫：大 n 前缀跳过
            skipped += 1
            continue
        o = opt_float(jobs[:jidx+1], m)
        r = ca/o
        if r > 1.15:
            hits.append((round(r, 5), p, l, jobs, m, jidx))
        if it % 30000 == 29999:
            print(f"it={it+1} {time.time()-t0:.0f}s hits={len(hits)} skipped={skipped}", flush=True)
    hits.sort(key=lambda x: -x[0])
    print(f"\n耗时 {time.time()-t0:.0f}s；事件 {len(hits)} 个（跳过 n>16: {skipped}）")
    for h in hits[:8]:
        print(f"  prefix_ratio={h[0]} t={h[1]} pi={h[2]} m={h[4]} jobs={h[3]}")
    with open("pocket2_prefix_hits.json", "w") as f:
        json.dump(hits[:50], f, ensure_ascii=False)

if __name__ == "__main__":
    main()
