"""fast_scan v2：证书缓存复用 + 手证 k 段剪枝。
优化4: 同 (m,k) 相邻 cnt 的证书大量重复——先用缓存 y 对新 rows 做廉价精确复核
       （支撑行算术，无 LP 求解），命中即免解 LP；未命中才解 LP 并更新缓存。
优化5: k=1（P2K1 手证）与 k>=m-2（P2K-top 手证）默认跳过（--full 保留全扫）。
迭代序：k 外 cnt 内（同 k 的 rows 大部分相同，缓存命中率高）。
"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fast_lp import rows_fixed, float_cert_rows, exact_verify_support
from pairing_feasible import bin_count_solutions

PROG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fast_scan2_progress.jsonl')
CERT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pocket2_osr_certs_v2.txt')


def task_group(arg):
    """同一 (m,k) 的全部 cnt：带缓存依次处理。返回记录列表。"""
    m, k, cnts = arg
    out = []
    cache = None   # (y_weights_Fraction, sup_names)
    for cnt in cnts:
        R, nv = rows_fixed(m, cnt, k, use_order=True)
        if cache is not None:
            yc, sup_names = cache
            # 用缓存证书直接复核：找同名行，验证 A^T y=0, bt^T y=0, bc^T y=-1
            from fractions import Fraction as F
            idx = {}
            for i, r in enumerate(R):
                idx.setdefault(r[3], []).append(i)
            if all(nm in idx for nm in sup_names):
                rows = [R[idx[nm][0]] for nm in sup_names]
                ok = all(sum(F(row[j]) * w for row, w in zip([r[0] for r in rows], yc)) == 0 for j in range(nv))
                ok = ok and sum(r[2] * w for r, w in zip(rows, yc)) == 0
                ok = ok and sum(r[1] * w for r, w in zip(rows, yc)) == -1
                if ok:
                    cert = [(nm, str(w)) for nm, w in zip(sup_names, yc)]
                    out.append({'m': m, 'cnt': cnt, 'k': k, 'cert': cert, 'reused': True})
                    continue
        yf = float_cert_rows(R, nv)
        if yf is None:
            out.append({'m': m, 'cnt': cnt, 'k': k, 'hole': True})
            continue
        y, sup = exact_verify_support(R, nv, yf)
        if y is None:
            out.append({'m': m, 'cnt': cnt, 'k': k, 'hole': True, 'ratfail': True})
            continue
        sup_names = [R[i][3] for i in sup]
        cache = (y, sup_names)
        cert = [(nm, str(w)) for nm, w in zip(sup_names, y)]
        out.append({'m': m, 'cnt': cnt, 'k': k, 'cert': cert})
    return out


if __name__ == '__main__':
    import concurrent.futures as cf
    import multiprocessing as mp
    full = '--full' in sys.argv
    m_lo, m_hi = 4, 30
    for a in sys.argv[1:]:
        if a.startswith('--m='):
            m_lo, m_hi = map(int, a[4:].split(','))
    jobs = []
    skipped = 0
    for m in range(m_lo, m_hi + 1):
        cnts = bin_count_solutions(m)
        for k in range(1, m):
            if not full and (k == 1 or k >= m - 2):
                skipped += len(cnts)
                continue
            jobs.append((m, k, cnts))
    print(f'任务组 {len(jobs)} 个 (m,k)（手证覆盖跳过 {skipped} 个 (cnt,k)）')
    t0 = time.time()
    holes, ncert, nreuse = [], 0, 0
    ctx = mp.get_context('spawn')
    with cf.ProcessPoolExecutor(max_workers=8, mp_context=ctx) as ex, \
            open(PROG, 'a') as fp, open(CERT, 'a') as fc:
        cur_m = None
        for recs in ex.map(task_group, jobs, chunksize=4):
            for rec in recs:
                if rec['m'] != cur_m:
                    cur_m = rec['m']
                    print(f'  m={cur_m} ... ({time.time()-t0:.0f}s)', flush=True)
                fp.write(json.dumps({k2: v for k2, v in rec.items() if k2 != 'cert'}) + '\n')
                if rec.get('hole'):
                    holes.append((rec['m'], rec['cnt'], rec['k'], rec.get('ratfail')))
                else:
                    fc.write(json.dumps(rec) + '\n')
                    ncert += 1
                    nreuse += 1 if rec.get('reused') else 0
    print(f'完成: 证书 {ncert}（复用命中 {nreuse}，LP 实解 {ncert-nreuse}）, 洞 {len(holes)}, 耗时 {time.time()-t0:.0f}s')
    print('洞:', holes[:15] if holes else '无 ✓')
