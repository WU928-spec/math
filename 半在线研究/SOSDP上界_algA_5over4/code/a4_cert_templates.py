"""razor 带证书支撑的系统提取与模板聚类（agent-4 方向2 第2步）。

对 razor 带各族（(1,m−3,0,1,0,0)、(2,m−5,0,1,1,0) 及邻近族），m ∈ {6,8,10,12,16,20,30}，
全 k，提取 build_v4（全合法行）精确证书支撑，按"权重形状"聚类，识别 m,k-均匀模板族。
输出：每个 (cnt族, k) 的支撑签名；同签名跨 m 是否一致（=> ∀m 模板候选）。
"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a4_razor_symbolic import build_v4
from farkas_fixed import float_cert, rationalize_verify
from pairing_feasible import bin_count_solutions
from fractions import Fraction as F
from collections import defaultdict


def cert_support(m, cnt, k):
    A, bc, bt, names, nv = build_v4(m, cnt, k)
    yf = float_cert(A, bc, bt)
    if yf is None:
        return None
    y, N = rationalize_verify(A, bc, bt, yf)
    if y is None:
        return 'RATFAIL'
    return [(names[i], y[i]) for i in range(len(y)) if y[i] != 0]


def signature(sup, m, cnt, k):
    """支撑 -> 模板签名：名字去索引（保留相对位置结构）+ 权重比例（×最小公倍缩放）。"""
    if sup is None or sup == 'RATFAIL':
        return str(sup)
    names = [n for n, _ in sup]
    ws = [w for _, w in sup]
    g = ws[0]
    rat = tuple(str(w / g) for w in ws)
    # 名字模式：替换数字为 #，但保留 srt/q1<=j/nofit 的具体索引相对 k 的信息
    import re
    pat = tuple(re.sub(r'\d+', '#', n) for n in names)
    return (pat, rat)


if __name__ == '__main__':
    t0 = time.time()
    fams = {
        'A(1,m-3,0,1,0,0)': lambda m: (1, m - 3, 0, 1, 0, 0),
        'B(2,m-5,0,1,1,0)': lambda m: (2, m - 5, 0, 1, 1, 0),
        'C(3,m-7,0,1,2,0)': lambda m: (3, m - 7, 0, 1, 2, 0),
        'D(2,m-5,0,2,1,1)': lambda m: (2, m - 5, 0, 2, 1, 1),
        'E(3,m-7,1,2,1,0)': lambda m: (3, m - 7, 1, 2, 1, 0),
    }
    for fname, mkcnt in fams.items():
        print(f'==== 族 {fname} ====', flush=True)
        sig_seen = defaultdict(list)
        for m in [6, 8, 10, 12, 16, 20, 30]:
            cnt = mkcnt(m)
            if min(cnt) < 0:
                continue
            for k in range(2, m):
                sup = cert_support(m, cnt, k)
                sg = signature(sup, m, cnt, k)
                sig_seen[sg].append((m, k))
        for sg, pts in sig_seen.items():
            pat, rat = sg if isinstance(sg, tuple) else (sg, ())
            ks = sorted(set(k for _, k in pts))
            ms = sorted(set(m for m, _ in pts))
            print(f'  模板({len(pts)}点 m∈{ms} k∈{ks}):')
            if isinstance(sg, tuple):
                print(f'    行名: {" ".join(pat)}')
                print(f'    权重比: {" ".join(rat)}')
            else:
                print(f'    {sg}')
        print(f'  ({time.time()-t0:.0f}s)', flush=True)
