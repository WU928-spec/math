"""口袋1/3 的 k>=2 证书模式收集：看是否存在与 (m,k) 无关的统一常数证书。"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pocket1_lp import build_p1, float_cert as fc1, rationalize_verify as rv1
from pocket3_lp import build_p3, float_cert as fc3, rationalize_verify as rv3

def show(build, fc, rv, tag, ms):
    print(f'==== {tag} ====')
    for m in ms:
        for k in range(2, m):
            A, bc, bt, names, nv = build(m, k)
            yf = fc(A, bc, bt)
            if yf is None:
                print(f'  m={m} k={k}: FEASIBLE!')
                continue
            y, N = rv(A, bc, bt, yf)
            if y is None:
                print(f'  m={m} k={k}: RATFAIL')
                continue
            parts = ' '.join(f'{names[i]}:{y[i]}' for i in range(len(y)) if y[i] != 0)
            print(f'  m={m} k={k}: {parts}')

if __name__ == '__main__':
    show(build_p1, fc1, rv1, '口袋1 k>=2', [4, 5, 6, 7, 8])
    show(build_p3, fc3, rv3, '口袋3 k>=2', [4, 5, 6, 7, 8])
