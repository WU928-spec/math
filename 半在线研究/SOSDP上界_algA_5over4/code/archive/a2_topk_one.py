"""topk_check 单 m 分片版（8min 硬顶合规）：python a2_topk_one.py <m>
k=1 用 base LP（P2K1 结论），k=m-2/m-1 用 build_close(mon2+ammin)（P2K-top 结论）。"""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from farkas_fixed import build_fixed, float_cert
from hole_close import build_close
from pairing_feasible import bin_count_solutions

m = int(sys.argv[1])
t0 = time.time()
cnts = bin_count_solutions(m)
bad1 = badtop = 0
for n, cnt in enumerate(cnts):
    A, bc, bt, names, nv = build_fixed(m, cnt, 1)
    if float_cert(A, bc, bt) is None:
        bad1 += 1
        print(f'  ✗ P2K1 反例? m={m} cnt={cnt}', flush=True)
    for k in (m - 2, m - 1):
        A, bc, bt, names, nv = build_close(m, cnt, k, use_ammin=True)
        if float_cert(A, bc, bt) is None:
            badtop += 1
            print(f'  ✗ P2K-top 反例? m={m} k={k} cnt={cnt}', flush=True)
    if (n + 1) % 100 == 0:
        print(f'  ... m={m} {n+1}/{len(cnts)} ({time.time()-t0:.0f}s) bad1={bad1} badtop={badtop}', flush=True)
rec = {'m': m, 'k1_bad': bad1, 'ktop_bad': badtop, 'n_cnt': len(cnts), 'sec': round(time.time() - t0)}
with open(f'topk_check_progress.jsonl', 'a') as f:
    f.write(json.dumps(rec) + '\n')
print(f'm={m}: k=1 反例 {bad1}/{len(cnts)}, k>=m-2 反例 {badtop} ({rec["sec"]}s)', flush=True)
