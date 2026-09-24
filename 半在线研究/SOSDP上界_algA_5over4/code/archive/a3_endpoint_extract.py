"""a3_endpoint_extract.py —— k=m−2（JJJ 墙）证书提取：值语言角落 + t+j₁+j₂≤1 假设行。
路线 A：V.build（值语言 A 系+B 系）+ A5(k=m−2)/LZ/HZ(k=m−2) + 假设行（j₁+j₂≤1−t）。
若全 m INF 且证书权重呈 (m)-generic 模式 ⟹ 拟合 ∀m 望远镜恒等式（a3_template_verify 管线）。
对照：机索引对枚举版（main_jjj_enum）的支撑行参考。
输出：a3_endpoint_kmm2.jsonl（每 m 一条：status + support + 整数权重）。
"""
import numpy as np
from scipy.optimize import linprog
from fractions import Fraction as F
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a1_value_lp2 as V
from main_cegar3 import MG
from fast_lp import float_cert_rows, exact_verify_support

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'a3_endpoint_kmm2.jsonl')


def build_kmm2(m, cnt):
    """值语言角落行（去 SJrev/S1v/JJrev；B4 保留——不指望它进支撑）+ A5/LZ/HZ @ k=m−2。"""
    nS = m - 1
    k = m - 2
    A, bc, bt, names, leg, nv = V.build(m, cnt, use_sjrev=False, use_s1v=False, use_jjrev=False)
    A, bc, bt, names = list(A), list(bc), list(bt), list(names)
    IP, IAM, IQ1 = 0, 1, 2
    vs = lambda r: 3 + (r - 1); vj = lambda r: 3 + nS + (r - 1)

    def con(row, c0, c1, nm):
        A.append([F(x) for x in row]); bc.append(F(c0)); bt.append(F(c1)); names.append(nm)

    for i in range(1, k + 1):
        row = [F(0)] * nv; row[IP] = 1; row[vs(i)] = -1; row[vj(nS - k + i)] = -1
        con(row, -MG, 0, f'A5_{i}')
    row = [F(0)] * nv; row[vs(k)] = 4; row[IAM] = -5; row[IQ1] = -1
    con(row, 0, 0, 'LZ')
    if k < nS:
        row = [F(0)] * nv; row[vs(k + 1)] = -4; row[IAM] = 5; row[IQ1] = 1
        con(row, -MG, 0, 'HZ')
    # 假设行（JJJ 墙假设，非法化目标）：t + j_1 + j_2 <= 1 ⟺ j_1+j_2 <= 1−t
    row = [F(0)] * nv; row[vj(1)] = 1; row[vj(2)] = 1
    con(row, F(1), F(-1), 'ASSUME_tj1j2')
    R = [([float(x) for x in row], bc[i], bt[i], names[i]) for i, row in enumerate(A)]
    return R, nv


def main():
    pf = open(OUT, 'w')
    t0 = time.time()
    for m in range(5, 13):
        for cnt in [(1, m - 3, 0, 1, 0, 0), (2, m - 5, 0, 1, 1, 0)]:
            if cnt[1] < 1:
                continue
            R, nv = build_kmm2(m, cnt)
            yf = float_cert_rows(R, nv)
            if yf is None:
                rec = dict(m=m, cnt=cnt, status='FEAS')
                print(f'm={m} cnt={cnt}: FEAS!!（角落+假设可行——JJJ 墙漏）', flush=True)
            else:
                y, sup = exact_verify_support(R, nv, yf)
                if y is None:
                    rec = dict(m=m, cnt=cnt, status='RATFAIL')
                    print(f'm={m} cnt={cnt}: RATFAIL', flush=True)
                else:
                    from math import gcd
                    from functools import reduce
                    den = reduce(lambda a, b: a * b // gcd(a, b), (w.denominator for w in y), 1)
                    ints = [int(w * den) for w in y]
                    g = reduce(gcd, (abs(x) for x in ints if x != 0))
                    iw = [x // g for x in ints]
                    supnames = [R[i][3] for i in sup]
                    rec = dict(m=m, cnt=cnt, status='OK',
                               support=supnames, weights=iw)
                    print(f'm={m} cnt0={cnt[0]}: OK 支撑 {list(zip(supnames, iw))}', flush=True)
            pf.write(json.dumps(rec) + '\n'); pf.flush()
    pf.close()
    print(f'({time.time()-t0:.0f}s)')


if __name__ == '__main__':
    main()
