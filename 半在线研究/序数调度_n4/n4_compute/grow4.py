import sys, os, json, time
sys.path.insert(0, "/mnt/agents/output/n4_compute")
from compute import *
from scan import summarize
out = "/mnt/agents/output/n4_compute/grow_n4.jsonl"
done = set()
if os.path.exists(out):
    for line in open(out):
        try: done.add(tuple(json.loads(line)["profile"]))
        except: pass
for m in [11, 12, 13]:
    c = (1,)*m
    if c in done: continue
    t0=time.time()
    res = minmax_profile(c, 4, verbose=False)
    s = summarize(res)
    open(out,"a").write(json.dumps(s)+"\n")
    print(f"(1^{m}) n=4 -> {s['minmax']:.6f}  [{time.time()-t0:.1f}s, {s['num_partitions']} parts]", flush=True)
