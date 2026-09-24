import itertools, math, json
from functools import lru_cache
sq = math.sqrt(37)
r = (2+sq)/11; s = (13+sq)/33; c = (1+sq)/6

# OPT via 计数DP（只有3种任务大小）
def opt_count(counts, m):
    vals = [1.0, r, s]
    lo, hi = max(vals[i] for i,k in enumerate(counts) if k>0), sum(vals[i]*k for i,k in enumerate(counts))
    def feasible(C):
        pats = [(a,b,cc) for a in range(counts[0]+1) for b in range(counts[1]+1) for cc in range(counts[2]+1)
                if a*vals[0]+b*vals[1]+cc*vals[2] <= C + 1e-12 and (a,b,cc)!=(0,0,0)]
        reach = {(0,0,0)}
        for _ in range(m):
            nxt = set()
            for (x,y,z) in reach:
                for (a,b,cc) in pats:
                    v = (x+a, y+b, z+cc)
                    if v[0]<=counts[0] and v[1]<=counts[1] and v[2]<=counts[2]: nxt.add(v)
            reach = nxt
        return tuple(counts) in reach
    for _ in range(40):
        mid = (lo+hi)/2
        if feasible(mid): hi = mid
        else: lo = mid
    return hi

def gv(seq, m):
    seq = list(map(float, seq)); K = len(seq)
    # 前缀 OPT：按值分组计数
    opts = []
    for i in range(1, K+1):
        pre = seq[:i]
        counts = [pre.count(1.0), pre.count(r), pre.count(s)]
        opts.append(opt_count(counts, m))
    @lru_cache(maxsize=None)
    def V(i, loads):
        if i == K: return 0.0
        best = None; seen = set()
        for b in range(m):
            lb = loads[b]
            if lb in seen: continue
            seen.add(lb)
            nl = sorted(loads, reverse=True); nl[b] += seq[i]; nl.sort(reverse=True)
            nl = tuple(round(v,9) for v in nl)
            pre = nl[0]/opts[i]
            if best is not None and pre >= best - 1e-12: continue
            val = max(pre, V(i+1, nl))
            if best is None or val < best: best = val
        return best
    return V(0, tuple([0.0]*m))

for m in (5, 6):
    seq = [1.0]*(m-1) + [r]*(m-1) + [s]*(m-1)
    v = gv(seq, m)
    print(json.dumps({"m": m, "n": len(seq), "game_value": v, "c": c, "diff": v-c}))
