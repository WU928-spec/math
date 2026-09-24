"""a3_ open 点匹配层分析：双墙躲开点（SS 对存在+JJJ 存在+角落约束）的装箱可行性判定。
对 main_jjj_enum 的 open (m,k,cnt) 与每个存活 hi 对 (u,v)：
角落 LP（保序+挤压+t+j_u+j_v≤1+SS01）可行点 + 装箱 DFS。
若可装箱 ⟹ (P) 反例；若不可装箱 ⟹ 匹配层失败机理（SJ 匹配/联合计数）。
"""
import numpy as np
from scipy.optimize import linprog
from fractions import Fraction as F
import sys, os, json, itertools, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fast_lp import rows_fixed
from audit_constraints import pack_exact


def build_open(m, cnt, k, u, v, use_ss01=True):
    nS = m - 1
    R, nv = rows_fixed(m, cnt, k, use_order=True)
    R = [r for r in R if r[3] not in ('SS', 'SJ', 'JJJ', 'JJ')]
    row = [0.0] * nv
    for i in range(nS):
        row[2 + i] = 1.0
        row[2 + nS + i] = 1.0
    R.append((row, F(m - 1), F(-1), 'squeeze'))
    # JJJ 对：t + j_u + j_v <= 1
    row = [0.0] * nv
    row[1] = 1.0
    row[2 + nS + u] = 1.0
    row[2 + nS + v] = 1.0
    R.append((row, F(1), F(0), 'JJpair'))
    if use_ss01:
        row = [0.0] * nv
        row[2] = 1.0
        row[3] = 1.0
        R.append((row, F(1), F(0), 'SS01'))
    return R, nv


def analyze(m, k, cnt, pairs, nS):
    """对每个存活对提取角落可行点并装箱判定。"""
    tl = (m - 1) / (4 * (m - 2))
    for u, v in pairs:
        R, nv = build_open(m, cnt, k, u, v)
        Af = np.array([r for r, _, _, _ in R])
        for t0 in np.linspace(tl + 0.002, 1 / 3, 6):
            bf = np.array([float(c0) + float(c1) * t0 for _, c0, c1, _ in R])
            res = linprog(c=np.zeros(nv), A_ub=Af, b_ub=bf, bounds=(None, None), method='highs')
            if res.status != 0:
                continue
            x = res.x
            s = x[2:2 + nS]
            j = x[2 + nS:2 + 2 * nS]
            fr = [F(str(vv)).limit_denominator(10**6) for vv in list(s) + list(j) + [x[1]]]
            pk = pack_exact(fr, m - 1)
            tag = '✗✗ 可装箱 (P) 反例!' if pk else '不可装箱'
            print(f'    对(j{u},j{v}) t={t0:.4f}: p={x[0]:.4f} p+t={x[0]+x[1]:.4f} {tag}')
            if pk:
                print(f'      s={np.round(s, 3)}')
                print(f'      j={np.round(j, 3)}')
                return True
    return False


def main():
    recs = [json.loads(l) for l in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'main_jjj_enum.jsonl'))]
    opens = [r for r in recs if r['tier'] == 'open']
    # 代表点：每个 m 的 k=2（hi 区最大）与 k=m−2（hi 区最小）
    picks = []
    for m in [7, 8, 10, 12, 16, 20]:
        ks = sorted({r['k'] for r in opens if r['m'] == m})
        for kk in [ks[0], ks[-1]] if ks else []:
            for cnt in [(1, m - 3, 0, 1, 0, 0), (2, m - 5, 0, 1, 1, 0)]:
                rr = [r for r in opens if r['m'] == m and r['k'] == kk and tuple(r['cnt']) == cnt]
                if rr:
                    picks.append((m, kk, cnt, rr[0]['feas_pairs'][:3]))
    t_start = time.time()
    nce = 0
    for m, k, cnt, pairs in picks:
        a, b, c, d, e, f = cnt
        if 2 * a + b + c != m - 1 or b + 3 * d + 2 * e + f != m:
            continue
        nS = m - 1
        print(f'm={m} k={k} cnt={cnt}（{len(pairs)} 对试）:')
        if analyze(m, k, cnt, pairs, nS):
            nce += 1
            print(f'  ⟹ (P) 反例发现于 m={m} k={k} cnt={cnt}！')
            break
    print(f'({time.time()-t_start:.0f}s) 反例数 = {nce}')


if __name__ == '__main__':
    main()
