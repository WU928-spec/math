import random, sys, heapq
from functools import lru_cache

def algA_fb(jobs, m):
    """returns (makespan, whether makespan machine's last job was a fallback)"""
    loads = [0.0]*m
    lastfb = [False]*m
    L = None
    for j, p in enumerate(jobs):
        if j < m:
            loads[j] += p; lastfb[j] = False
        else:
            if j == m:
                L = jobs[m-1] + jobs[m]
            cap = 1.25*L
            best = -1
            for i in range(m):
                if loads[i] + p <= cap + 1e-12 and (best < 0 or loads[i] > loads[best]):
                    best = i
            if best >= 0:
                loads[best] += p; lastfb[best] = False
            else:
                mn = min(range(m), key=lambda i: loads[i])
                loads[mn] += p; lastfb[mn] = True
    mi = max(range(m), key=lambda i: loads[i])
    return loads[mi], lastfb[mi]

def opt_jobs(jobs, m):
    n = len(jobs); tot = sum(jobs)
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
    for _ in range(40):
        mid = (lo+hi)/2
        if can(mid): hi = mid
        else: lo = mid
    return hi

seed = int(sys.argv[1]); random.seed(seed)
heaps = {m: [] for m in (3,4,5,6)}
def gen(m):
    n = random.randint(m+1, 11)
    mode = random.random()
    if mode < 0.35:
        jobs = [round(random.uniform(0.2, 1.0), 4) for _ in range(n)]
    elif mode < 0.6:
        jobs = [random.randint(1, 12) for _ in range(n)]
    elif mode < 0.8:
        B = random.uniform(0.6, 1.0); b = random.uniform(0.3, B); L = B + b
        jobs = [round(random.uniform(0.5*B, B),4) for _ in range(m)] + [round(random.uniform(0.2, 0.55)*L, 4) for _ in range(n-m)]
    else:
        t = random.uniform(0.25, 0.6); k = random.randint(m, n)
        jobs = [1.0]*k + [round(t,4)]*(n-k)
    return sorted(jobs, reverse=True)

N = int(sys.argv[2])
for _ in range(N):
    m = random.choice((3,4,5,6))
    jobs = gen(m)
    a, fb = algA_fb(jobs, m)
    if not fb: continue
    L = jobs[m-1] + jobs[m]
    lb = max(sum(jobs)/m, jobs[0], L)
    cr = a/lb
    h = heaps[m]
    if len(h) < 60: heapq.heappush(h, (cr, jobs))
    elif cr > h[0][0]: heapq.heapreplace(h, (cr, jobs))

out = open(f"/mnt/agents/output/m4_search/algA_fb_{seed}.txt","w")
for m in (3,4,5,6):
    cands = sorted(heaps[m], key=lambda x:-x[0])[:25]
    besttrue=0; bestjobs=None; ba=bo=0
    for cr, jobs in cands:
        o = opt_jobs(jobs, m); a,_ = algA_fb(jobs, m)
        if a/o > besttrue: besttrue=a/o; bestjobs=jobs; ba,bo=a,o
    out.write(f"m={m}: max FALLBACK ratio = {besttrue:.8f}  algA={ba:.5f} opt={bo:.5f}\n  jobs={bestjobs}\n")
out.close()
print("done", seed)
