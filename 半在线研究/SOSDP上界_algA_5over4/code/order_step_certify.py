"""保序 LP 精确化：口袋2 m=18..20 二步残留（tiered ghost）的逐 (m,cnt,k,jj2,h) 精确证书。
h 枚举是 case split：必须全部 h 精确 INFEASIBLE 才算闭合。证书落盘 + 独立复验。
"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from order_step import build_fixed3
from second_step import build_fixed2
from farkas_fixed import float_cert, rationalize_verify

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pocket2_order_certificates.txt')

RESIDUALS = [
    (18, (3, 11, 0, 1, 2, 0), 15), (18, (3, 11, 0, 1, 2, 0), 16), (18, (3, 11, 0, 1, 2, 0), 17),
    (19, (3, 12, 0, 1, 2, 0), 16), (19, (3, 12, 0, 1, 2, 0), 17), (19, (3, 12, 0, 1, 2, 0), 18),
    (20, (3, 13, 0, 1, 2, 0), 17), (20, (3, 13, 0, 1, 2, 0), 18), (20, (3, 13, 0, 1, 2, 0), 19),
]

if __name__ == '__main__':
    t0 = time.time()
    ncert = 0
    fails = []
    with open(OUT, 'w') as f:
        for m, cnt, k in RESIDUALS:
            nS = m - 1
            jj = k - 1
            rem2 = []
            for j2 in range(nS):
                if j2 == jj:
                    continue
                A, bc, bt, names, nv = build_fixed2(m, cnt, k, jj2=j2)
                if float_cert(A, bc, bt) is None:
                    rem2.append(j2)
            for j2 in rem2:
                for h in range(nS + 1):
                    A, bc, bt, names, nv = build_fixed3(m, cnt, k, j2, h)
                    yf = float_cert(A, bc, bt)
                    if yf is None:
                        fails.append((m, cnt, k, j2, h, 'feasible'))
                        continue
                    y, N = rationalize_verify(A, bc, bt, yf)
                    if y is None:
                        fails.append((m, cnt, k, j2, h, 'ratfail'))
                        continue
                    nz = [(names[i], str(y[i])) for i in range(len(y)) if y[i] != 0]
                    f.write(json.dumps({'m': m, 'cnt': cnt, 'k': k, 'jj2': j2, 'h': h,
                                        'cert': nz}) + '\n')
                    ncert += 1
            print(f'm={m} cnt={cnt} k={k}: jj2={rem2} × h=0..{nS} 精确化完成 ({time.time()-t0:.0f}s)')
    print(f'证书数 {ncert} -> {OUT}')
    print('失败:', fails if fails else '无（全部 h 精确闭合 ✓）')
