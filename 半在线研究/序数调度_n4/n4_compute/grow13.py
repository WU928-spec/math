import sys, os, json, time
sys.path.insert(0, "/mnt/agents/output/n4_compute")
from compute import *
from scan import summarize
out = "/mnt/agents/output/n4_compute/grow_n4.jsonl"
t0=time.time()
res = minmax_profile((1,)*13, 4, verbose=True)
s = summarize(res)
open(out,"a").write(json.dumps(s)+"\n")
print(f"(1^13) n=4 -> {s['minmax']:.6f}  [{time.time()-t0:.1f}s, {s['num_partitions']} parts]", flush=True)
