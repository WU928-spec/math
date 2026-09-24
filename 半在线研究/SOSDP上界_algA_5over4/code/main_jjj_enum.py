"""main_ razor 带 k<m−1 段修复扫描：junior 对枚举（合法版 JJJ 墙）。
背景：agent-3 的 JJJ01 行引用低端区 j0,j1，在 k<m−1（hi 区非空、junior 无序）不是
全池最小两件 ⟹ 行不合法（main 敌意复核，BOARD 2026-09-23 裁决条）。
合法替代品 = 对枚举：
  JJJ 存在 ⟺ t+全池最小两 junior≤1 ⟺ ∃对(i,i'): t+j_i+j_{i'}≤1。
  Tier1: 对每一对，corner+t+j_i+j_{i'}≤1 全 INF ⟹ 角落 ⟹ JJJ 不存在 ⟹ (P) 单墙闭合。
  Tier2（Tier1 失败点）: 每对加 SS01(s0+s1≤1, 全域合法) 联合 INF ⟹ 析取双墙闭合
         （对假设是 case 分情形，不是必要行——逻辑合法）。
输出：main_jjj_enum.jsonl 每 (m,cnt,k) 一条（断点续跑）；RATFAIL/FEAS-pair 列表落盘。
"""
import numpy as np
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fast_lp import rows_fixed, float_cert_rows, exact_verify_support
from fractions import Fraction as F

PROGRESS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'main_jjj_enum.jsonl')


def base_rows(m, cnt, k):
    nS = m - 1
    R, nv = rows_fixed(m, cnt, k, use_order=True)
    R = [r for r in R if r[3] not in ('SS', 'SJ', 'JJJ', 'JJ')]
    row = [0.0] * nv
    for i in range(nS):
        row[2 + i] = 1.0
        row[2 + nS + i] = 1.0
    R.append((row, F(m - 1), F(-1), 'squeeze'))
    return R, nv, nS


def pair_row(nv, nS, i, j):
    row = [0.0] * nv
    row[1] = 1.0
    row[2 + nS + i] = 1.0
    row[2 + nS + j] = 1.0
    return (row, F(1), F(0), f'JJJ_{i}_{j}')


def ss01_row(nv):
    row = [0.0] * nv
    row[2] = 1.0
    row[3] = 1.0
    return (row, F(1), F(0), 'SS01')


def lp_inf(R, nv):
    """(is_infeasible_exact, ratfail)。float 找到证书→精确复核支撑；None→按可行处理。"""
    yf = float_cert_rows(R, nv)
    if yf is None:
        return False, False
    y, sup = exact_verify_support(R, nv, yf)
    return (y is not None), (y is None)


def scan(m_lo=4, m_hi=20):
    done = set()
    if os.path.exists(PROGRESS):
        with open(PROGRESS) as f:
            for line in f:
                try:
                    r = json.loads(line)
                    done.add((r['m'], tuple(r['cnt']), r['k']))
                except Exception:
                    pass
    pf = open(PROGRESS, 'a')
    t0 = time.time()
    stat = {'closed1': 0, 'closed2': 0, 'open': 0}
    for m in range(m_lo, m_hi + 1):
        cnts = [(1, m - 3, 0, 1, 0, 0), (2, m - 5, 0, 1, 1, 0)]
        for cnt in cnts:
            a, b, c, d, e, f = cnt
            if 2 * a + b + c != m - 1 or b + 3 * d + 2 * e + f != m:
                continue
            for k in range(2, m - 1):  # k=2..m−2（k=1、k=m−1 已由合法行闭合）
                if (m, cnt, k) in done:
                    continue
                R0, nv, nS = base_rows(m, cnt, k)
                feas_pairs, nrat = [], 0
                for i in range(nS):
                    for j in range(i + 1, nS):
                        inf, rat = lp_inf(R0 + [pair_row(nv, nS, i, j)], nv)
                        nrat += rat
                        if not inf and not rat:
                            feas_pairs.append((i, j))
                if not feas_pairs:
                    tier = 'closed1'
                else:
                    R1 = R0 + [ss01_row(nv)]
                    feas2 = []
                    for (i, j) in feas_pairs:
                        inf, rat = lp_inf(R1 + [pair_row(nv, nS, i, j)], nv)
                        nrat += rat
                        if not inf and not rat:
                            feas2.append((i, j))
                    tier = 'open' if feas2 else 'closed2'
                    feas_pairs = feas2
                stat[tier] += 1
                rec = {'m': m, 'cnt': cnt, 'k': k, 'tier': tier,
                       'n_pairs': nS * (nS - 1) // 2, 'feas_pairs': feas_pairs,
                       'ratfail': nrat}
                pf.write(json.dumps(rec) + '\n')
                pf.flush()
                if tier != 'closed1':
                    print(f'  {tier} m={m} cnt={cnt} k={k} 存活对 {feas_pairs[:8]}{"..." if len(feas_pairs)>8 else ""}', flush=True)
        print(f'  m={m} 完成（{time.time()-t0:.0f}s，累计 {stat}）', flush=True)
    print(f'扫描结束 {stat}（{time.time()-t0:.0f}s）')


if __name__ == '__main__':
    scan()
