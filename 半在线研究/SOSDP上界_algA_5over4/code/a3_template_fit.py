"""a3_template_fit.py —— 任务③模板机第一步：115 证书的支撑约束极小整数证书提取+模式分组。
对每点：重建 noSJrev 行集 + A5/LZ/HZ，取支撑行子集，解 A_sup^T w=0 ∧ bc_sup^T w=-1
（分数精确，sympy 高斯消元），归一为最小正整数向量，按 cnt 分组打印权重模式，
寻找 (m,k) 参数化的统一证书结构。
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fractions import Fraction as F
from math import gcd
from functools import reduce
import a1_value_lp2 as V
from main_cegar3 import MG
from a3_cert115_weights import build


def solve_support(R, sup_names):
    """支撑行上的精确证书：解 A^T w=0, bc^T w=-1, bt^T w=0。返回 w（Fraction 列表）或 None。"""
    idx = [i for i, r in enumerate(R) if r[3] in sup_names]
    rows = [R[i] for i in idx]
    names = [r[3] for r in rows]
    nvar = len(R[0][0])
    nw = len(rows)
    # 方程组：对每变量 sum_r w_r A_r[v]=0（nvar 个），sum w_r bc_r=-1，sum w_r bt_r=0
    M = []
    for v in range(nvar):
        M.append([F(row[0][v]) for row in rows] + [F(0)])
    M.append([F(row[1]) for row in rows] + [F(-1)])
    M.append([F(row[2]) for row in rows] + [F(0)])
    # 高斯消元（行阶梯，分数）
    M = [list(r) for r in M]
    nrow, ncol = len(M), nw
    piv = []
    r0 = 0
    for c in range(ncol):
        p = None
        for rr in range(r0, nrow):
            if M[rr][c] != 0:
                p = rr; break
        if p is None:
            continue
        M[r0], M[p] = M[p], M[r0]
        pv = M[r0][c]
        M[r0] = [x / pv for x in M[r0]]
        for rr in range(nrow):
            if rr != r0 and M[rr][c] != 0:
                f = M[rr][c]
                M[rr] = [x - f * y for x, y in zip(M[rr], M[r0])]
        piv.append(c)
        r0 += 1
        if r0 == nrow:
            break
    # 检查相容性与自由变量
    for rr in range(r0, nrow):
        if all(M[rr][c] == 0 for c in range(ncol)) and M[rr][ncol] != 0:
            return None, None
    free = [c for c in range(ncol) if c not in piv]
    if len(free) > 1:
        return None, ('free', len(free))
    w = [F(0)] * ncol
    for i, c in enumerate(piv):
        w[c] = M[i][ncol]
    if free:
        # 单自由变量：取使 bc^T w=-1 成立的值（已由方程强制）；置 0 看相容
        c = free[0]
        # 若 bc 行非主元行则其已强制 w[c]
        # 直接从消元结果读：非主元列变量任取——取使一切方程成立的值由方程组决定：
        # 单自由时方程组欠定；用 bc^T w=-1 反解
        # 重新直接解：令 w[c]=λ，w[piv_i]=M[i][ncol]-λ*M[i][c]
        # 由 bc 行（已被消元兼容）无法定 λ——改用非负+整数最小化：λ 由 w>=0 区间取分数中点
        lo, hi = None, None
        for i, pc in enumerate(piv):
            a = M[i][c]; b = M[i][ncol]
            if a > 0:
                h = -b / a
                hi = h if hi is None or h < hi else hi
            elif a < 0:
                l = -b / a
                lo = l if lo is None or l > lo else lo
        lam = lo if lo is not None and lo > 0 else (hi if hi is not None and hi > 0 else (lo if lo is not None else F(0)))
        for i, pc in enumerate(piv):
            w[pc] = M[i][ncol] - lam * M[i][c]
        w[c] = lam
    return w, names


def to_int_weights(w):
    den = reduce(lambda a, b: a * b // gcd(a, b), (x.denominator for x in w), 1)
    ints = [int(x * den) for x in w]
    g = reduce(gcd, (abs(x) for x in ints if x != 0))
    return [x // g for x in ints]


def main():
    pts = []
    for l in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'a3_cert115_weights.jsonl')):
        r = json.loads(l)
        if r['status'] == 'OK':
            pts.append(r)
    groups = {}
    for r in pts:
        m, cnt, k = r['m'], r['cnt'], r['k']
        R, nv = build(m, cnt, k, dict(use_sjrev=False, use_s1v=False, use_jjrev=False))
        sup = set(r['support'])
        w, names = solve_support(R, sup)
        if w is None:
            print(f'm={m} cnt0={cnt[0]} k={k}: 解失败 {names}')
            continue
        iw = to_int_weights(w)
        key = (cnt[0], tuple(names))
        groups.setdefault(key, []).append((m, k, dict(zip(names, iw))))
    print(f'\n签名组数：{len(groups)}')
    for key, lst in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        cnt0, names = key
        print(f'\n== cnt0={cnt0} 组（{len(lst)} 点）==')
        for m, k, wd in lst[:6]:
            print(f'  m={m} k={k}: ' + ' '.join(f'{n}={v}' for n, v in wd.items()))


if __name__ == '__main__':
    main()
