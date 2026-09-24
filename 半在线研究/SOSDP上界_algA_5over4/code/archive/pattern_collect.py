"""收集口袋2角落证书模式：按 (cnt,k) 族归纳，看权重与索引如何随参数走。
输出按 cnt 分组，每组内列 k=1..m-1 的证书非零约束（名字+权重×1253 取整）。
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from farkas_constant import build_frac, float_cert, rationalize_verify
from pairing_feasible import bin_count_solutions
from fractions import Fraction

D = 1253  # 公分母（经验）

def cert_of(m, cnt, k):
    A, bc, bt, names, nv = build_frac(m, cnt, k)
    yf = float_cert(A, bc, bt)
    if yf is None:
        return None
    y, N = rationalize_verify(A, bc, bt, yf)
    if y is None:
        return 'RATIONALIZE_FAIL'
    return [(names[i], y[i]) for i in range(len(y)) if y[i] != 0]

if __name__ == '__main__':
    for m in [7, 10]:
        cnts = bin_count_solutions(m)
        print(f'==== m={m}: {len(cnts)} 种 cnt ====')
        for cnt in cnts:
            a, b, c, d, e, f = cnt
            print(f'-- cnt=(SS{a},SJ{b},S{c},JJJ{d},JJ{e},J{f}) --')
            for k in range(1, m):
                cert = cert_of(m, cnt, k)
                if cert is None:
                    print(f'   k={k}: FEASIBLE!')
                    continue
                if cert == 'RATIONALIZE_FAIL':
                    print(f'   k={k}: RATFAIL')
                    continue
                parts = ' '.join(f'{nm}:{int(w*D) if w*D == int(w*D) else w}' for nm, w in cert)
                print(f'   k={k}: {parts}')
