import sys, itertools, time, json
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
BUDGET = 900
t0 = time.time(); out = []
fout = open('/mnt/agents/output/m4_search/fine334.jsonl','w')
fams = [(3,4),(2,5),(4,4),(3,5)]
for nb, nc in fams:
    for b in np.arange(0.55, 0.951, 0.01):
        for cc in np.arange(0.30, min(b,0.75)+0.001, 0.01):
            if time.time()-t0 > BUDGET: break
            v = gv([1,1,1]+[round(b,3)]*nb+[round(cc,3)]*nc)
            out.append((v, round(b,3), round(cc,3), nb, nc))
            if v >= 1.15:
                fout.write(json.dumps({"V":round(v,6),"b":round(b,3),"c":round(cc,3),"nb":nb,"nc":nc})+"\n"); fout.flush()
        if time.time()-t0 > BUDGET: break
    if time.time()-t0 > BUDGET: break
out.sort(reverse=True)
fout.write(json.dumps({"SUMMARY": True, "tested": len(out), "top": [[round(v,6),b,cc,nb,nc] for v,b,cc,nb,nc in out[:10]]})+"\n")
fout.close()
