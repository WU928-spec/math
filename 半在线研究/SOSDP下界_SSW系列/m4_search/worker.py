
import sys, itertools, time, json, random
from functools import lru_cache
import numpy as np

FAMILY, BUDGET, OUT, SEED = sys.argv[1], float(sys.argv[2]), sys.argv[3], int(sys.argv[4])
random.seed(SEED); np.random.seed(SEED)
M = 4
_MCache = {}
def opt_f(seq):
    n = len(seq)
    if n == 1: return float(seq[0])
    key = n
    if key not in _MCache:
        A = np.array(list(itertools.product(range(M), repeat=n-1)))
        _MCache[key] = np.eye(M)[A]
    oh = _MCache[key]
    ld = (oh * np.asarray(seq[1:], float)[None,:,None]).sum(1)
    ld[:,0] += seq[0]
    return float(ld.max(1).min())

def gv(seq):
    seq = sorted(map(float, seq), reverse=True); K = len(seq)
    opts = [opt_f(seq[:i+1]) for i in range(K)]
    @lru_cache(maxsize=None)
    def V(i, loads):
        if i == K: return 0.0
        best = None; seen = set()
        for b in range(M):
            lb = loads[b]
            if lb in seen: continue
            seen.add(lb)
            nl = list(loads); nl[b] += seq[i]; nl.sort(reverse=True)
            nl = tuple(round(v, 9) for v in nl)
            pre = nl[0]/opts[i]
            if best is not None and pre >= best: continue
            val = max(pre, V(i+1, nl))
            if best is None or val < best: best = val
        return best
    return V(0, tuple([0.0]*M))

def grid(a, b, s):
    out = []; v = a
    while v <= b + 1e-9: out.append(round(v,4)); v += s
    return out

def gen():
    # 产出 (family_tag, seq) 流
    if FAMILY == 'F3':      # (1,1,1,1, f, s×k)
        for f in grid(0.2, 1.0, 0.05):
            for s in grid(0.1, f, 0.05):
                for k in (3,4,5):
                    yield 'F3', [1,1,1,1,f]+[s]*k
    elif FAMILY == 'F2':    # (x,x,x,1-x, f, s×k)
        for x in grid(0.5, 0.85, 0.025):
            for f in grid(0.15, 1-x, 0.05):
                for s in grid(0.1, f, 0.05):
                    for k in (3,4):
                        yield 'F2', [x,x,x,1-x,f]+[s]*k
    elif FAMILY == 'F4':    # 开场变体: (1,1,1,t) / (1,1,1,1,y*4) / (1,1,1,t,t) 等
        for t in grid(0.2, 1.0, 0.025):
            yield 'F4a', [1,1,1,t]
            yield 'F4b', [1,1,1,t,t]
            yield 'F4c', [1,1,1,1,t,t,t,t]
            yield 'F4d', [1,1,1,1,t,t,t,t,t]
            for s in grid(0.1, t, 0.1):
                yield 'F4e', [1,1,1,t,s,s,s,s]
    elif FAMILY == 'R2':    # 随机两值族
        while True:
            a = round(random.uniform(0.3,1.0),3); b = round(random.uniform(0.05,a),3)
            na = random.randint(3,6); nb = random.randint(2,6)
            if na+nb > 10: continue
            yield 'R2', [a]*na+[b]*nb
    elif FAMILY == 'R3':    # 随机三值族
        while True:
            vs = sorted([round(random.uniform(0.05,1.0),3) for _ in range(3)], reverse=True)
            ns = [random.randint(1,5) for _ in range(3)]
            if sum(ns) > 10: continue
            seq = [v for v,k in zip(vs,ns) for _ in range(k)]
            yield 'R3', seq
    else:                   # R4: 随机一般递减序列
        while True:
            n = random.randint(6,9)
            yield 'R4', sorted([round(random.uniform(0.05,1.0),3) for _ in range(n)], reverse=True)

t0 = time.time(); cnt = 0; top = []
fout = open(OUT, 'w')
for tag, seq in gen():
    if time.time()-t0 > BUDGET: break
    if len(seq) > 10: continue
    try:
        v = gv(seq)
    except Exception:
        continue
    cnt += 1
    if v >= 1.10:
        rec = {"fam": tag, "seq": seq, "V": round(v,6)}
        fout.write(json.dumps(rec)+"\n"); top.append((v, tag, seq))
    if cnt % 200 == 0:
        fout.flush()
top.sort(reverse=True)
fout.write(json.dumps({"SUMMARY": True, "tested": cnt, "top": [[round(v,6), t, s] for v,t,s in top[:8]]})+"\n")
fout.close()
