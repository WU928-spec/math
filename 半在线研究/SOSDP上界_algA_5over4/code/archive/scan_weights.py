"""扫描口袋2角落常数证书的权重随 m 的规律（为大 m 渐近参数化做准备）。"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from farkas_constant import build_frac, float_cert, rationalize_verify


if __name__ == '__main__':
    print('各 m 常数证书的非零约束权重（看 m 规律）:')
    for m in range(4, 16):
        nS = m - 1
        A, bc, bt, names, nv = build_frac(m, (1, m - 3, 0, 1, 0, 0), 1)
        yf = float_cert(A, bc, bt)
        if yf is None:
            print(f'  m={m}: feasible（无证书）')
            continue
        y, N = rationalize_verify(A, bc, bt, yf)
        if y is None:
            print(f'  m={m}: 有理化失败')
            continue
        parts = []
        for i in range(len(y)):
            if y[i] != 0:
                w = y[i]
                parts.append(f'{names[i]}={w.numerator}/{w.denominator}')
        print(f'  m={m:2d} ({sum(1 for v in y if v != 0)}条): ' + '  '.join(parts))
