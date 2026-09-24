"""口袋2一步 LP 证书生成：build_fixed，m=4..11 全 cnt 全 k，精确常数证书 -> pocket2_certificates.jsonl。
统一格式：{"builder":"build_fixed","m":..,"cnt":[..],"k":..,"N":..,"y":[[idx,"num/den"],...]}
"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from farkas_fixed import build_fixed, float_cert, rationalize_verify
from pairing_feasible import bin_count_solutions

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pocket2_certificates.jsonl')

if __name__ == '__main__':
    t0 = time.time()
    n_cert = n_fail = 0
    with open(OUT, 'w') as f:
        for m in range(4, 12):
            cnts = bin_count_solutions(m)
            for k in range(1, m):
                for cnt in cnts:
                    A, bc, bt, names, nv = build_fixed(m, cnt, k)
                    yf = float_cert(A, bc, bt)
                    y = N = None
                    if yf is not None:
                        y, N = rationalize_verify(A, bc, bt, yf)
                    if y is None:
                        n_fail += 1
                        print(f'  失败 m={m} cnt={cnt} k={k}（{"无float证书" if yf is None else "有理化失败"}）', flush=True)
                        continue
                    n_cert += 1
                    f.write(json.dumps({'builder': 'build_fixed', 'm': m, 'cnt': list(cnt),
                                        'k': k, 'N': N,
                                        'y': [[i, str(y[i])] for i in range(len(y)) if y[i] != 0]}) + '\n')
            print(f'm={m} 完成（累计证书 {n_cert}，{time.time()-t0:.0f}s）', flush=True)
    print(f'结束: {n_cert} 份证书, {n_fail} 失败 -> {OUT}')
