"""全称量词检查：口袋2角落 LP 是否对【所有】箱型计数 cnt × 所有 k 都有证书？
farkas_constant.py 主循环只查"存在某 cnt 有证书"——若角落闭合需全称，则那是假阳性。
本脚本逐 (m,k,cnt) 报 feasible/cert，找出所有 feasible 洞。
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from farkas_constant import build_frac, float_cert, rationalize_verify
from pairing_feasible import bin_count_solutions

if __name__ == '__main__':
    holes = []
    for m in range(4, 13):
        cnts = bin_count_solutions(m)
        for k in range(1, m):
            ncert = nfeas = 0
            for cnt in cnts:
                A, bc, bt, names, nv = build_frac(m, cnt, k)
                yf = float_cert(A, bc, bt)
                if yf is None:
                    nfeas += 1
                    holes.append((m, k, cnt))
                else:
                    y, N = rationalize_verify(A, bc, bt, yf)
                    if y is not None:
                        ncert += 1
                    else:
                        nfeas += 1
                        holes.append((m, k, cnt, 'rationalize_fail'))
            tag = '' if nfeas == 0 else f'  <<< {nfeas} 个洞'
            if nfeas:
                print(f'm={m} k={k}: cert={ncert} feasible={nfeas}/{len(cnts)}{tag}')
    print(f'\n总洞数: {len(holes)}')
    for h in holes[:40]:
        print('  洞:', h)
