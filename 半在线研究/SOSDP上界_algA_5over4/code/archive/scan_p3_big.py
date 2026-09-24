"""口袋3大 m 扫描：build_p3f，m=13..30 全 k=1..m-1，float_cert + rationalize_verify 精确验证。
断点续跑：已完成 (m,k) 存 p3_big_scan.jsonl，重跑跳过。
用法: python scan_p3_big.py [m_lo m_hi]
"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pocket13_fixed import build_p3f
from farkas_fixed import float_cert, rationalize_verify

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'p3_big_scan.jsonl')


def done_set():
    done = set()
    if os.path.exists(OUT):
        with open(OUT) as f:
            for line in f:
                try:
                    r = json.loads(line)
                    done.add((r['m'], r['k']))
                except Exception:
                    pass
    return done


def ablate(names, A, bc, bt, drop_names):
    """去掉名字在 drop_names 中的约束后重新求 float 证书；None=feasible。"""
    idx = [i for i, n in enumerate(names) if n not in drop_names]
    return float_cert([A[i] for i in idx], [bc[i] for i in idx], [bt[i] for i in idx])


if __name__ == '__main__':
    m_lo = int(sys.argv[1]) if len(sys.argv) > 1 else 13
    m_hi = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    done = done_set()
    print(f'口袋3大m扫描 m={m_lo}..{m_hi}，已完成 {len(done)} 发，输出 {OUT}', flush=True)
    t0 = time.time()
    n_new = 0
    stats = {'OK': 0, 'FEAS': 0, 'RATFAIL': 0}
    for m in range(m_lo, m_hi + 1):
        for k in range(1, m):
            if (m, k) in done:
                continue
            A, bc, bt, names, nv = build_p3f(m, k)
            yf = float_cert(A, bc, bt)
            if yf is None:
                rec = {'m': m, 'k': k, 'status': 'FEAS'}
                stats['FEAS'] += 1
            else:
                y, N = rationalize_verify(A, bc, bt, yf)
                if y is None:
                    rec = {'m': m, 'k': k, 'status': 'RATFAIL'}
                    stats['RATFAIL'] += 1
                else:
                    cert = [[names[i], str(y[i])] for i in range(len(y)) if y[i] != 0]
                    rec = {'m': m, 'k': k, 'status': 'OK', 'N': N, 'cert': cert}
                    stats['OK'] += 1
            with open(OUT, 'a') as f:
                f.write(json.dumps(rec) + '\n')
            n_new += 1
            if n_new % 25 == 0:
                el = time.time() - t0
                print(f'  进度 m={m} k={k} 新发 {n_new} 耗时 {el:.0f}s stats={stats}', flush=True)
        print(f'm={m} 完成 (累计 {n_new} 发, {time.time()-t0:.0f}s)', flush=True)
    print(f'扫描结束: {stats}', flush=True)

    # ---- 消融抽查（INFEASIBLE 结论纪律）：对代表 (m,k)，去掉关键约束必须变 feasible ----
    print('消融抽查（基准均有精确证书）:', flush=True)
    for m, k in [(m_lo, 1), ((m_lo + m_hi) // 2, (m_lo + m_hi) // 4), (m_hi, m_hi - 1)]:
        A, bc, bt, names, nv = build_p3f(m, k)
        base = float_cert(A, bc, bt)
        assert base is not None, f'm={m},k={k} 基准无证书!'
        r1 = 'feasible ✓' if ablate(names, A, bc, bt, {'vol<=m'}) is None else '仍INFEAS!'
        r2 = 'feasible ✓' if ablate(names, A, bc, bt, {'y>=1-2t'}) is None else '仍INFEAS!'
        r3 = 'feasible ✓' if ablate(names, A, bc, bt, {'x>=t'}) is None else '仍INFEAS!'
        mach_names = {n for n in names if n.startswith('mach')}
        some_mach = {sorted(mach_names)[len(mach_names) // 2]}
        r4 = 'feasible ✓' if ablate(names, A, bc, bt, some_mach) is None else '仍INFEAS!'
        print(f'  m={m} k={k}: 去vol->{r1} 去y>=1-2t->{r2} 去x>=t->{r3} 去1个mach->{r4}', flush=True)
