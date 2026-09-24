import itertools, json
from functools import lru_cache
import numpy as np
_MCache = {}
def opt_f(seq, m=4):
    n = len(seq)
    if n == 1: return float(seq[0])
    if n not in _MCache:
        A = np.array(list(itertools.product(range(m), repeat=n-1)))
        _MCache[n] = np.eye(m)[A]
    oh = _MCache[n]
    ld = (oh * np.asarray(seq[1:], float)[None,:,None]).sum(1)
    ld[:,0] += seq[0]
    return float(ld.max(1).min())
def gv(seq):
    seq = list(map(float, seq)); K = len(seq)
    opts = [opt_f(seq[:i+1]) for i in range(K)]
    @lru_cache(maxsize=None)
    def V(i, loads):
        if i == K: return 0.0
        best = None; seen = set()
        for b in range(4):
            lb = loads[b]
            if lb in seen: continue
            seen.add(lb)
            nl = list(loads); nl[b] += seq[i]; nl.sort(reverse=True)
            pre = nl[0]/opts[i]
            if best is not None and pre >= best: continue
            val = max(pre, V(i+1, tuple(nl)))
            if best is None or val < best: best = val
        return best
    return V(0, (0.0,0.0,0.0,0.0))
import math
sq = math.sqrt(37)
r = (2+sq)/11; s = (13+sq)/33
c = (1+sq)/6
res = []
res.append(('exact-333', gv([1,1,1,r,r,r,s,s,s])))
res.append(('exact-334', gv([1,1,1,r,r,r,s,s,s,s])))
res.append(('exact-335', gv([1,1,1,r,r,r,s,s,s,s,s])))
# 局部细扫 0.002 步长
best=(0,None)
for rr in np.arange(0.726, 0.744, 0.002):
    for ss in np.arange(0.566, min(rr,0.590), 0.002):
        v = gv([1,1,1,round(rr,4)]*1 + [round(rr,4)]*2 + [round(ss,4)]*3)
        if v > best[0]: best = (v, round(rr,4), round(ss,4))
res.append(('fine-best', best))
print(json.dumps({"c": c, "r": r, "s": s, "results": res}))
