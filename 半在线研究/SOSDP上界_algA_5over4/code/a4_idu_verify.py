"""万能 7 行恒等式 IDU 的 razor 全族验证（agent-4）。"""
import sys, time
sys.path.insert(0, 'code' if __name__ == '__main__' else '.')
from fractions import Fraction as F
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from a4_symbolic_verify import check_identity

IDU = [(('j1>=t', 0), F(2)), (('danger', 0), F(6)), (('pair0', 0), F(4)), (('pair1', 0), F(2)),
       (('srt0', 0), F(1)), (('XSS0', 0), F(3)), (('XTRI', 0), F(4))]

FAMS = {
    'A(1,m-3,0,1,0,0)': lambda m: (1, m - 3, 0, 1, 0, 0),
    'B(2,m-5,0,1,1,0)': lambda m: (2, m - 5, 0, 1, 1, 0),
    'C(3,m-7,0,1,2,0)': lambda m: (3, m - 7, 0, 1, 2, 0),
    'D(2,m-5,0,2,1,1)': lambda m: (2, m - 5, 0, 2, 1, 1),
    'E(3,m-7,1,2,1,0)': lambda m: (3, m - 7, 1, 2, 1, 0),
    'F(4,m-9,0,1,3,0)': lambda m: (4, m - 9, 0, 1, 3, 0),
    'G(5,m-11,0,1,4,0)': lambda m: (5, m - 11, 0, 1, 4, 0),
}

if __name__ == '__main__':
    t0 = time.time()
    for fn, mk in FAMS.items():
        bad = []
        for m in range(6, 51):
            cnt = mk(m)
            if min(cnt) < 0:
                continue
            for k in range(2, m):
                ok, r = check_identity(m, cnt, k, IDU)
                if not ok:
                    bad.append((m, k, r))
        status = '全通过 ✓' if not bad else f'{len(bad)} 处失败 例 {bad[:3]}'
        print(f'{fn}: m=6..50 全 k  {status}  ({time.time()-t0:.0f}s)', flush=True)
