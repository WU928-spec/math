"""提取洞区精确证书并对比 m 间的结构：若证书支撑与系数随 m 有规律，
则可写统一符号证书（对全 m>=12  sympy 验证），把逐 m LP 升级为全 m 证明。"""
from fractions import Fraction as F
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from farkas_fixed import float_cert, rationalize_verify
from hole_close import build_close


def exact_cert(m, cnt, k):
    A, bc, bt, names, nv = build_close(m, cnt, k)
    yf = float_cert(A, bc, bt)
    if yf is None:
        return None, None, None
    y, N = rationalize_verify(A, bc, bt, yf)
    return y, names, (A, bc, bt)


def show(m, cnt, k):
    y, names, _ = exact_cert(m, cnt, k)
    if y is None:
        print(f'm={m} k={k} cnt={cnt}: 无证书')
        return
    print(f'=== m={m} k={k} cnt={cnt}: 非零证书项 ===')
    for nm, v in zip(names, y):
        if v != 0:
            print(f'   {nm:16s} {v}')


if __name__ == '__main__':
    for m in [12, 13, 14]:
        show(m, (2, m - 5, 0, 1, 1, 0), m - 1)
