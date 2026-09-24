"""口袋2二步 LP 大 m 扫描：m=21..30 一步洞（取自 p2_holes_big.jsonl）枚举 jj2 判二步。

断点续跑：p2_s2_prog_{shard}.jsonl 记录已判 (m,cnt,k,jj2)；
闭合精确证书 -> p2_s2_certs_{shard}.jsonl（统一格式：builder+参数+稀疏权重）；
残留洞（含可行点结构）-> p2_s2_holes_{shard}.jsonl。
用法: python scan_p2_s2_big.py SHARD M1 [M2 ...]
"""
import sys, os, json, time
import numpy as np
from scipy.optimize import linprog
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from farkas_fixed import float_cert, rationalize_verify
from second_step import build_fixed2

HERE = os.path.dirname(os.path.abspath(__file__))


def primal_point2(m, cnt, k, jj2):
    """二步 LP 可行点：A x <= bc + bt·t，bt 并入 t 列（变量1）。"""
    A, bc, bt, names, nv = build_fixed2(m, cnt, k, jj2=jj2)
    Af = np.array([[float(x) for x in row] for row in A])
    bcf = np.array([float(x) for x in bc])
    btf = np.array([float(x) for x in bt])
    A2 = Af.copy(); A2[:, 1] -= btf
    res = linprog(c=np.zeros(nv), A_ub=A2, b_ub=bcf, bounds=(None, None), method='highs')
    return (res.x, Af, bcf, btf, names) if res.status == 0 else (None, None, None, None, None)


def hole_record(m, cnt, k, jj2):
    x, Af, bcf, btf, names = primal_point2(m, cnt, k, jj2)
    if x is None:
        return {'m': m, 'cnt': list(cnt), 'k': k, 'jj2': jj2, 'primal_feasible': False}
    viol = float(np.max(Af @ x - bcf - btf * x[1]))
    nS = m - 1
    p, t = float(x[0]), float(x[1])
    s = [round(float(v), 5) for v in x[2:2 + nS]]
    j = [round(float(v), 5) for v in x[2 + nS:2 + 2 * nS]]
    am, q1, q2 = float(x[2 + 2 * nS]), float(x[2 + 2 * nS + 1]), float(x[2 + 2 * nS + 2])
    return {'m': m, 'cnt': list(cnt), 'k': k, 'jj2': jj2, 'primal_feasible': True,
            'max_viol': viol, 'p': round(p, 5), 't': round(t, 6), 'p_plus_t': round(p + t, 5),
            'am': round(am, 5), 'q1': round(q1, 5), 'q2': round(q2, 5),
            'K': round(1.25 * (am + q1), 5), 's': s, 'j': j}


if __name__ == '__main__':
    shard = sys.argv[1]
    ms = set(int(x) for x in sys.argv[2:])
    PROG = os.path.join(HERE, f'p2_s2_prog_{shard}.jsonl')
    CERTS = os.path.join(HERE, f'p2_s2_certs_{shard}.jsonl')
    HOLES = os.path.join(HERE, f'p2_s2_holes_{shard}.jsonl')

    onestep = []
    for line in open(os.path.join(HERE, 'p2_holes_big.jsonl')):
        h = json.loads(line)
        if h['m'] in ms:
            onestep.append((h['m'], tuple(h['cnt']), h['k']))
    onestep.sort()
    print(f'shard {shard}: {len(onestep)} 个一步洞 (m={sorted(ms)})', flush=True)

    done = set()
    if os.path.exists(PROG):
        for line in open(PROG):
            r = json.loads(line)
            done.add((r['m'], tuple(r['cnt']), r['k'], r['jj2']))
    print(f'已判 {len(done)} 个 jj2，续跑。', flush=True)

    t0 = time.time()
    n_closed = n_hole = n_ratfail = 0
    for (m, cnt, k) in onestep:
        nS = m - 1
        jj = k - 1
        hole_jj2 = []
        for j2 in range(nS):
            if j2 == jj or (m, cnt, k, j2) in done:
                continue
            A, bc, bt, names, nv = build_fixed2(m, cnt, k, jj2=j2)
            yf = float_cert(A, bc, bt)
            if yf is None:
                st = 'hole'
            else:
                y, N = rationalize_verify(A, bc, bt, yf)
                if y is None:
                    st = 'ratfail'
                else:
                    st = 'closed'
                    rec = {'builder': 'build_fixed2', 'm': m, 'cnt': list(cnt), 'k': k,
                           'jj2': j2, 'N': N,
                           'y': [[i, str(y[i])] for i in range(len(y)) if y[i] != 0]}
                    with open(CERTS, 'a') as f:
                        f.write(json.dumps(rec) + '\n')
            if st == 'hole':
                hr = hole_record(m, cnt, k, j2)
                with open(HOLES, 'a') as f:
                    f.write(json.dumps(hr) + '\n')
                hole_jj2.append(j2)
                n_hole += 1
            elif st == 'ratfail':
                n_ratfail += 1
                hole_jj2.append((j2, 'ratfail'))
            else:
                n_closed += 1
            with open(PROG, 'a') as f:
                f.write(json.dumps({'m': m, 'cnt': list(cnt), 'k': k, 'jj2': j2, 'status': st}) + '\n')
        print(f'  m={m} k={k} cnt={cnt}: 残留 jj2={hole_jj2 if hole_jj2 else "无（全闭合）"} '
              f'({time.time()-t0:.0f}s)', flush=True)
    print(f'shard {shard} 结束: 闭合 {n_closed}, 残留洞 {n_hole}, ratfail {n_ratfail}, '
          f'用时 {time.time()-t0:.0f}s', flush=True)
