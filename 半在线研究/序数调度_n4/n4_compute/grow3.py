import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from compute import *
from scan import summarize
out = "grow_n3.jsonl"
done = set()
if os.path.exists(out):
    for line in open(out):
        try: done.add(tuple(json.loads(line)["profile"]))
        except: pass
for m in [10, 11, 12]:
    c = (1,)*m
    if c in done: continue
    t0=time.time()
    res = minmax_profile(c, 3, verbose=False)
    s = summarize(res)
    open(out,"a").write(json.dumps(s)+"\n")
    print(f"(1^{m}) n=3 -> {s['minmax']:.6f}  [{time.time()-t0:.1f}s, {s['num_partitions']} parts]", flush=True)
