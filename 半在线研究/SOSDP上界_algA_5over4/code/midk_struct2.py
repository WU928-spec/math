"""精确打印 b=0 / JJJ含t / mid-k 证书的行号与行内容（消歧重复命名）。"""
from fractions import Fraction as F
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from farkas_fixed import build_fixed, float_cert, rationalize_verify


def show(m, cnt, k):
    A, bc, bt, names, nv = build_fixed(m, cnt, k)
    yf = float_cert(A, bc, bt)
    if yf is None:
        print(f'm={m} k={k} cnt={cnt}: feasible')
        return
    y, N = rationalize_verify(A, bc, bt, yf)
    nS = m - 1
    def vs(i): return 2 + i
    def vj(i): return 2 + nS + i
    print(f'=== m={m} k={k} cnt={cnt} ===')
    for i, (nm, v) in enumerate(zip(names, y)):
        if v == 0:
            continue
        row = A[i]
        terms = []
        for j, c in enumerate(row):
            if c != 0:
                vn = ('p' if j == 0 else 't' if j == 1 else
                      (f's{j-2}' if j < 2 + nS else
                       (f'j{j-2-nS}' if j < 2 + 2 * nS else ('am' if j == 2 + 2 * nS else 'q1'))))
                terms.append(f'{c}{vn}')
        print(f'   [{i:3d}] {nm:12s} w={str(v):12s} | {"+".join(terms)} <= {bc[i]}{"+t*" + str(bt[i]) if bt[i] else ""}')


if __name__ == '__main__':
    show(12, (4, 0, 3, 4, 0, 0), 11)
    show(13, (4, 0, 4, 4, 0, 0), 12)
