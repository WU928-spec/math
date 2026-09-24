"""a3_ razor 带 (P) 收官证明：全域扫描（角落+保序+挤压+s0+s1<=1 是否 INF）。
闭合链（全部合法必要条件）：
  非装箱约束（§1 表 22 条 + mon2 保序）+ 挤压行（Σℓᵢ≤m−1−t）+ s₀+s₁≤1（SS 对存在必要条件）。
若 razor 带全 (m,k,cnt) INF ⟺ LP 可行域 ⊆ {s₀+s₁>1} ⟹ 角落点恒 s₀+s₁>1 ⟹ SS 对不存在
⟹ 计数恒等式 a=d+e+f≥1 矛盾 ⟹ 装箱不可能 ⟹ (P) 闭合。
断点续跑：a3_Prazor_scan.jsonl。
"""
import numpy as np
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fast_lp import rows_fixed, float_cert_rows, exact_verify_support
from fractions import Fraction as F

PROGRESS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'a3_Prazor_scan.jsonl')
CERTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'a3_Prazor_certs.txt')


def build_case(m, cnt, k):
    nS = m - 1
    R, nv = rows_fixed(m, cnt, k, use_order=True)
    R = [r for r in R if r[3] not in ('SS', 'SJ', 'JJJ', 'JJ')]
    row = [0.0] * nv
    for i in range(nS):
        row[2 + i] = 1.0
        row[2 + nS + i] = 1.0
    R.append((row, F(m - 1), F(-1), 'squeeze'))
    row = [0.0] * nv
    row[1] = 1.0
    row[2 + nS + 0] = 1.0
    row[2 + nS + 1] = 1.0
    R.append((row, F(1), F(0), 'JJJ01'))
    row = [0.0] * nv
    row[2] = 1.0
    row[3] = 1.0
    R.append((row, F(1), F(0), 'SS01'))
    return R, nv


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
    cf = open(CERTS, 'a')
    t_start = time.time()
    ninf = nfeas = nrat = 0
    for m in range(m_lo, m_hi + 1):
        cnts = [(1, m - 3, 0, 1, 0, 0), (2, m - 5, 0, 1, 1, 0)]
        mok = True
        for cnt in cnts:
            a, b, c, d, e, f = cnt
            if 2 * a + b + c != m - 1 or b + 3 * d + 2 * e + f != m:
                continue
            for k in range(1, m):
                if (m, cnt, k) in done:
                    continue
                R, nv = build_case(m, cnt, k)
                yf = float_cert_rows(R, nv)
                if yf is None:
                    rec = {'m': m, 'cnt': cnt, 'k': k, 'status': 'FEAS'}
                    nfeas += 1
                    mok = False
                    print(f'  ✗ FEAS（洞!）m={m} cnt={cnt} k={k}', flush=True)
                else:
                    y, sup = exact_verify_support(R, nv, yf)
                    if y is None:
                        rec = {'m': m, 'cnt': cnt, 'k': k, 'status': 'RATFAIL'}
                        nrat += 1
                        mok = False
                    else:
                        rec = {'m': m, 'cnt': cnt, 'k': k, 'status': 'OK'}
                        ninf += 1
                        if m <= 12:
                            names = [r[3] for r in R]
                            cf.write(json.dumps({'m': m, 'cnt': cnt, 'k': k,
                                                 'cert': {names[i]: str(w) for i, w in zip(sup, y)}}) + '\n')
                            cf.flush()
                pf.write(json.dumps(rec) + '\n')
                pf.flush()
        print(f'  m={m}: {"全闭 ✓" if mok else "有洞 ✗"}  （累计 INF {ninf}、洞 {nfeas}、RATFAIL {nrat}、{time.time()-t_start:.0f}s）', flush=True)
    print(f'扫描结束：INF {ninf}、洞 {nfeas}、RATFAIL {nrat}')
    print('结论:', 'razor 带 (P) 全域闭合（角落点恒 s₀+s₁>1 ⟹ SS 不存在 ⟹ 装箱不可能）' if nfeas == 0 and nrat == 0 else '有洞——报告')


if __name__ == '__main__':
    scan()
