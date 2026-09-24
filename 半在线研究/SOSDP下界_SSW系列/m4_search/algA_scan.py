import random, sys
from functools import lru_cache

def algA(jobs, m):
    loads = [0.0]*m
    L = None
    for j, p in enumerate(jobs):
        if j < m:
            loads[j] += p
        else:
            if j == m:
                L = jobs[m-1] + jobs[m]
            cap = 1.25*L
            best = -1
            for i in range(m):
                if loads[i] + p <= cap + 1e-12 and (best < 0 or loads[i] > loads[best]):
                    best = i
            if best >= 0:
                loads[best] += p
            else:
                mn = min(range(m), key=lambda i: loads[i])
                loads[mn] += p
    return max(loads)

def opt_jobs(jobs, m):
    n = len(jobs)
    tot = sum(jobs)
    lb = max(tot/m, max(jobs))
    subsum = [0.0]*(1<<n)
    for mask in range(1, 1<<n):
        lsb = mask & (-mask)
        subsum[mask] = subsum[mask^lsb] + jobs[lsb.bit_length()-1]
    def can(cap):
        @lru_cache(maxsize=None)
        def dfs(mask, k):
            if mask == 0: return True
            if k == 0: return False
            if subsum[mask] > k*cap + 1e-9: return False
            sub = mask
            while sub:
                if subsum[sub] <= cap + 1e-9 and dfs(mask^sub, k-1):
                    return True
                sub = (sub-1) & mask
            return False
        return dfs((1<<n)-1, m)
    lo, hi = lb, tot
    for _ in range(45):
        mid = (lo+hi)/2
        if can(mid): hi = mid
        else: lo = mid
    return hi

random.seed(int(sys.argv[1]) if len(sys.argv)>1 else 42)
best = {}  # m -> [ratio, jobs]
def consider(jobs, m):
    jobs = sorted(jobs, reverse=True)
    if len(jobs) < m+1: return
    a = algA(jobs, m); o = opt_jobs(jobs, m)
    r_ = a/o
    if m not in best or r_ > best[m][0]:
        best[m] = [r_, jobs, a, o]

N = int(sys.argv[2]) if len(sys.argv)>2 else 20000
for m in (3,4,5,6):
    for _ in range(N):
        n = random.randint(m+1, 11)
        mode = random.random()
        if mode < 0.35:
            jobs = [round(random.uniform(0.2, 1.0), 3) for _ in range(n)]
        elif mode < 0.6:
            jobs = [random.randint(1, 12) for _ in range(n)]
        elif mode < 0.8:
            # structured: m big jobs + medium jobs around (B+b)/4..(B+b)/2
            B = random.uniform(0.6, 1.0); b = random.uniform(0.3, B)
            L = B + b
            jobs = [B]*m + [round(random.uniform(0.2, 0.55)*L, 4) for _ in range(n-m)]
        else:
            # two-level: k copies of 1, rest copies of t
            t = random.uniform(0.25, 0.6)
            k = random.randint(m, n)
            jobs = [1.0]*k + [round(t,4)]*(n-k)
        consider(jobs, m)

with open(f"/mnt/agents/output/m4_search/algA_extremal_{sys.argv[1] if len(sys.argv)>1 else 42}.txt","w") as f:
    for m in sorted(best):
        r_, jobs, a, o = best[m]
        f.write(f"m={m}: ratio={r_:.8f} algA={a:.6f} opt={o:.6f}\n  jobs={jobs}\n")
print("done")
