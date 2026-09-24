import itertools, time, json
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
BUDGET = 780
t0 = time.time(); out = []
fout = open('/mnt/agents/output/m4_search/scan2.jsonl','w')
def rec(tag, seq):
    v = gv(seq); out.append((v, tag, [round(q,4) for q in seq]))
    if v >= 1.15: fout.write(json.dumps({"V":round(v,6),"tag":tag,"seq":[round(q,4) for q in seq]})+"\n"); fout.flush()
# T1: 互补族 (x×3, (1-x)×3, (1/3)×3)
for x in np.arange(0.5, 0.851, 0.0125):
    rec('T1', [round(x,4)]*3 + [round(1-x,4)]*3 + [1/3]*3)
# T2: (x×3, (1-x)×3, (1/4)×4)
for x in np.arange(0.5, 0.851, 0.0125):
    rec('T2', [round(x,4)]*3 + [round(1-x,4)]*3 + [0.25]*4)
# T3: (1×3, r×3, s×3) 细扫
for r in np.arange(0.66, 0.801, 0.005):
    for s in np.arange(0.50, min(r,0.62)+0.001, 0.005):
        if time.time()-t0 > BUDGET*0.75: break
        rec('T3', [1,1,1,round(r,4),round(r,4),round(r,4)]+[round(s,4)]*3)
# T4: (1×3, r×3, s×4) 细扫
for r in np.arange(0.66, 0.801, 0.005):
    for s in np.arange(0.45, min(r,0.62)+0.001, 0.005):
        if time.time()-t0 > BUDGET: break
        rec('T4', [1,1,1,round(r,4),round(r,4),round(r,4)]+[round(s,4)]*4)
out.sort(reverse=True)
fout.write(json.dumps({"SUMMARY": True, "tested": len(out), "top": [[round(v,6),t,s] for v,t,s in out[:10]]})+"\n")
fout.close()
