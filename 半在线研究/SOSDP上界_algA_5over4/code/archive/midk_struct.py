"""中段/leftover 区证书结构勘探：对 k<b+2、b=0、JJJ含t 的代表 (cnt,k)，
提取基线 LP（build_fixed，这些区域基线已闭合）精确证书支撑，找统一模式。
对照：同 m 的洞区（k>=b+2）证书 = 我的模板（danger/pair01/SS/JJJ/j>=t/mon2 链）。
"""
from fractions import Fraction as F
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from farkas_fixed import build_fixed, float_cert, rationalize_verify
from pairing_feasible import bin_count_solutions
from uniform_hole_cert import covered


def exact_support(m, cnt, k):
    A, bc, bt, names, nv = build_fixed(m, cnt, k)
    yf = float_cert(A, bc, bt)
    if yf is None:
        return None, None
    y, N = rationalize_verify(A, bc, bt, yf)
    if y is None:
        return None, None
    return names, [(nm, v) for nm, v in zip(names, y) if v != 0]


def show(m, cnt, k, tag=''):
    names, sup = exact_support(m, cnt, k)
    if sup is None:
        print(f'm={m} k={k} cnt={cnt} {tag}: 无证书(feasible?)')
        return
    print(f'=== m={m} k={k} cnt={cnt} {tag} ===')
    for nm, v in sup:
        print(f'   {nm:16s} {v}')


if __name__ == '__main__':
    m = 12
    cnts = bin_count_solutions(m)
    # leftover 代表：b=0 的第一个 cnt；k<b+2 的代表；JJJ含t cnt=(1,9,0,1,0,0)
    b0 = [c for c in cnts if c[1] == 0][:2]
    jjtt = [c for c in cnts if c == (1, m - 3, 0, 1, 0, 0)]
    ksmall = [c for c in cnts if c[1] >= 1 and c[3] >= 1 and not covered(c, m, 2)][:2]
    print('--- b=0 代表 ---')
    for cnt in b0:
        show(m, cnt, m - 1, 'b=0')
    print('--- JJJ含t ---')
    for cnt in jjtt:
        show(m, cnt, m - 1, 'JJJ含t')
    print('--- mid-k (k=2, k<b+2) ---')
    for cnt in ksmall:
        show(m, cnt, 2, 'mid-k2')
        show(m, cnt, 3, 'mid-k3' if not covered(cnt, m, 3) else '')
