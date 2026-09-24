import sys, os, json, time
sys.path.insert(0, "/mnt/agents/output/n4_compute")
from compute import minmax_profile
from scan import summarize
reps = [(4,4,3),(3,4,4),(3,3,5),(5,3,3),(2,3,3,3),(3,3,3,2),(2,2,3,4),(2,2,2,5),
        (1,1,1,2,2,4),(1,1,2,2,2,3),(1,1,1,3,3,2),(1,1,1,1,1,6),(2,2,2,2,2,1),(2,2,2,2,3),
        (2,1,1,1,1,1,1,1,1,1),(1,1,1,1,1,1,1,1,1,2)]
out = "/mnt/agents/output/n4_compute/scan_n4_m11.jsonl"
done = set()
if os.path.exists(out):
    for line in open(out):
        try: done.add(tuple(json.loads(line)["profile"]))
        except: pass
for c in reps:
    if c in done: continue
    t0=time.time()
    res = minmax_profile(c, 4, verbose=False)
    s = summarize(res)
    open(out,"a").write(json.dumps(s)+"\n")
    print(f"{c} -> {s['minmax']:.6f} [{time.time()-t0:.1f}s, {s['num_partitions']} parts]", flush=True)
