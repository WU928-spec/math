"""口袋2 一步+保序 快速全扫：m=31..45 扩扫（管线同 fast_scan.py，独立进度/证书文件，
不触碰 m=4..30 的 fast_scan_progress.jsonl / pocket2_onestep_order_certs.txt）。
8 spawn workers，断点续跑；洞若有则立即打印。
"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fast_lp import rows_fixed, float_cert_rows, exact_verify_support
from pairing_feasible import bin_count_solutions

PROG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fast_scan_progress_31_45.jsonl')
CERT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pocket2_onestep_order_certs_31_45.txt')


def task(arg):
    m, cnt, k = arg
    R, nv = rows_fixed(m, cnt, k, use_order=True)
    yf = float_cert_rows(R, nv)
    if yf is None:
        return {'m': m, 'cnt': cnt, 'k': k, 'hole': True}
    y, sup = exact_verify_support(R, nv, yf)
    if y is None:
        return {'m': m, 'cnt': cnt, 'k': k, 'hole': True, 'ratfail': True}
    cert = [(R[i][3], str(w)) for i, w in zip(sup, y)]
    return {'m': m, 'cnt': cnt, 'k': k, 'cert': cert}


if __name__ == '__main__':
    import concurrent.futures as cf
    import multiprocessing as mp
    m_lo = int(sys.argv[1]) if len(sys.argv) > 1 else 31
    m_hi = int(sys.argv[2]) if len(sys.argv) > 2 else 45
    done = set()
    if os.path.exists(PROG):
        for line in open(PROG):
            r = json.loads(line)
            done.add((r['m'], tuple(r['cnt']), r['k']))
    jobs = []
    for m in range(m_lo, m_hi + 1):
        for cnt in bin_count_solutions(m):
            for k in range(1, m):
                if (m, cnt, k) not in done:
                    jobs.append((m, cnt, k))
    print(f'待办 {len(jobs)} 个 (m,cnt,k)（已完成 {len(done)}）', flush=True)
    t0 = time.time()
    TIMEBOX = float(os.environ.get('A4_SCAN_TIMEBOX', '440'))  # 8min 硬顶自退
    holes = []
    ncert = 0
    ctx = mp.get_context('spawn')
    with cf.ProcessPoolExecutor(max_workers=2, mp_context=ctx) as ex, \
            open(PROG, 'a') as fp, open(CERT, 'a') as fc:
        cur_m = None
        for rec in ex.map(task, jobs, chunksize=32):
            if rec['m'] != cur_m:
                cur_m = rec['m']
                print(f'  m={cur_m} ... ({time.time()-t0:.0f}s)', flush=True)
            fp.write(json.dumps({k: v for k, v in rec.items() if k != 'cert'}) + '\n')
            if rec.get('hole'):
                holes.append((rec['m'], rec['cnt'], rec['k'], rec.get('ratfail')))
                print(f'  !!! 洞 m={rec["m"]} cnt={rec["cnt"]} k={rec["k"]} '
                      f'ratfail={rec.get("ratfail")}', flush=True)
            else:
                fc.write(json.dumps(rec) + '\n')
                ncert += 1
            if (len(holes) + ncert) % 500 == 0:
                fp.flush(); fc.flush()
            if time.time() - t0 > TIMEBOX:
                fp.flush(); fc.flush()
                print(f'  时间盒自退：本轮新证 {ncert}，洞 {len(holes)}，断点已落盘 '
                      f'({time.time()-t0:.0f}s)', flush=True)
                ex.shutdown(wait=False, cancel_futures=True)
                sys.exit(0)
    print(f'完成: 证书 {ncert} 份, 洞 {len(holes)} 个, 耗时 {time.time()-t0:.0f}s')
    print('洞:', holes[:30] if holes else f'无——口袋2 m={m_lo}..{m_hi} 一步+保序全闭 ✓')
