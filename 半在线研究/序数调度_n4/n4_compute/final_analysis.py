"""final_analysis.py - build leaderboard tables from all scan JSONLs."""
import json, os, sys
p = '/mnt/agents/output/n4_compute/'

def load(path):
    out = []
    if not os.path.exists(path):
        return out
    with open(path) as f:
        for line in f:
            try:
                d = json.loads(line)
            except Exception:
                continue
            if 'error' not in d and 'minmax' in d:
                out.append(d)
    return out

def dedupe(ds):
    byp = {}
    for d in ds:
        byp.setdefault((tuple(d['profile']), d['n']), d)
    return list(byp.values())

n3 = dedupe(load(p + 'scan_n3.jsonl'))
n4 = dedupe(load(p + 'scan_n4.jsonl') + load(p + 'scan_n4_m11.jsonl') + load(p + 'grow_n4.jsonl'))
n5 = dedupe(load(p + 'scan_n5.jsonl'))

print('counts: n3', len(n3), 'n4', len(n4), 'n5', len(n5))
for tag, data in [('n=3', n3), ('n=4', n4)]:
    print(f'\n=== {tag}: max min-max by m ===')
    bym = {}
    for d in data:
        bym.setdefault(d['m'], []).append(d)
    for m in sorted(bym):
        ds = sorted(bym[m], key=lambda d: -d['minmax'])
        print(f"m={m:2d} (profiles={len(ds):4d}): max={ds[0]['minmax']:.6f}  {ds[0]['profile']}")

print('\n=== n=4 top 15 overall ===')
for d in sorted(n4, key=lambda d: -d['minmax'])[:15]:
    print(f"{d['minmax']:.6f}  m={d['m']}  {d['profile']}  {d['best_partition']}")

print('\n=== n=5 ===')
for d in n5:
    print(f"{d['minmax']:.6f}  {d['profile']}  {d['best_partition']}")
