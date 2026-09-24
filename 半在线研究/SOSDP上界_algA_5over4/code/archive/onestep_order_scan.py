"""一步+保序（无二步）全扫：m=12..20 全 cnt 全 k 全 h，float 快扫 + jsonl 断点续跑。
确认简化结构（一步+保序）在该范围无洞。精确化在确认后补。
"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from farkas_fixed import build_fixed, float_cert
from order_step import add_order
from pairing_feasible import bin_count_solutions

PROG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'onestep_order_progress.jsonl')

if __name__ == '__main__':
    done = set()
    if os.path.exists(PROG):
        for line in open(PROG):
            r = json.loads(line)
            done.add((r['m'], tuple(r['cnt']), r['k']))
    fout = open(PROG, 'a')
    t0 = time.time()
    holes = []
    for m in range(12, 21):
        cnts = bin_count_solutions(m)
        nS = m - 1
        for k in range(1, m):
            for cnt in cnts:
                if (m, cnt, k) in done:
                    continue
                bad = []
                for h in range(nS + 1):
                    A, bc, bt, names, nv = build_fixed(m, cnt, k)
                    A, bc, bt, names, nv = add_order(A, bc, bt, names, nv, nS, h)
                    if float_cert(A, bc, bt) is None:
                        bad.append(h)
                rec = {'m': m, 'cnt': cnt, 'k': k, 'hole_h': bad}
                fout.write(json.dumps(rec) + '\n')
                if bad:
                    holes.append((m, cnt, k, bad))
            fout.flush()
        print(f'm={m} 完成 ({time.time()-t0:.0f}s, 累计洞 {len(holes)})', flush=True)
    fout.close()
    print('总结:', '一步+保序 m=12..20 无洞 ✓' if not holes else f'{len(holes)} 个洞: {holes[:10]}')
