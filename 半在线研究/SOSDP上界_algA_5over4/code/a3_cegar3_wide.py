"""a3_cegar3_wide.py —— 任务②：main_cegar3 固定 t 网格扫描扩程到 m=17..50。
两 cnt 族 × k=2..m−3 × 两档（full / noSJrev=去SJrev,S1v,JJrev）× tmesh（与 main 一致）。
断点：a3_cegar3_wide.jsonl（每 (m,cnt,k,tier) 一条，可断点续跑）。
判读：全 INF ⟹ 154 模式扩至 m=50（无 m 效应）；FEAS 点逐个上报待查。
"""
import numpy as np
from scipy.optimize import linprog
from fractions import Fraction as F
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a1_value_lp2 as V
from main_cegar3 import MG

TMESH = [0.27, 0.29, 0.30, 0.31, 0.32, 0.33, 1 / 3]
TIERS = [('full', {}), ('noSJrev', dict(use_sjrev=False, use_s1v=False, use_jjrev=False))]


def build_k(m, cnt, k, kw):
    nS = m - 1
    A, bc, bt, names, leg, nv = V.build(m, cnt, **kw)
    A, bc, bt = list(A), list(bc), list(bt)
    IP, IAM, IQ1 = 0, 1, 2
    vs = lambda r: 3 + (r - 1); vj = lambda r: 3 + nS + (r - 1)
    for i in range(1, k + 1):
        row = [F(0)] * nv; row[IP] = 1; row[vs(i)] = -1; row[vj(nS - k + i)] = -1
        A.append(row); bc.append(-MG); bt.append(F(0))
    row = [F(0)] * nv; row[vs(k)] = 4; row[IAM] = -5; row[IQ1] = -1
    A.append(row); bc.append(F(0)); bt.append(F(0))
    if k < nS:
        row = [F(0)] * nv; row[vs(k + 1)] = -4; row[IAM] = 5; row[IQ1] = 1
        A.append(row); bc.append(-MG); bt.append(F(0))
    Af = np.array([[float(x) for x in row] for row in A])
    bcf = np.array([float(x) for x in bc])
    btf = np.array([float(x) for x in bt])
    return Af, bcf, btf, nv


def scan_point(m, cnt, k, kw):
    Af, bcf, btf, nv = build_k(m, cnt, k, kw)
    for t0 in TMESH:
        res = linprog(c=np.zeros(nv), A_ub=Af, b_ub=bcf + btf * t0,
                      bounds=(None, None), method='highs')
        if res.status == 0:
            return t0
    return None


def main():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'a3_cegar3_wide.jsonl')
    done = set()
    if os.path.exists(path):
        for l in open(path):
            try:
                r = json.loads(l); done.add((r['m'], tuple(r['cnt']), r['k'], r['tier']))
            except Exception:
                pass
        print(f'断点 {len(done)}，续跑', flush=True)
    pf = open(path, 'a')
    t0 = time.time(); ninf = nfeas = 0
    for m in range(17, 51):
        mok = True
        for cnt in [(1, m - 3, 0, 1, 0, 0), (2, m - 5, 0, 1, 1, 0)]:
            for k in range(2, m - 2):
                for tier, kw in TIERS:
                    if (m, tuple(cnt), k, tier) in done:
                        continue
                    f = scan_point(m, cnt, k, kw)
                    pf.write(json.dumps(dict(m=m, cnt=cnt, k=k, tier=tier,
                                             status='INF' if f is None else f'FEAS@{f:.3f}')) + '\n')
                    pf.flush()
                    if f is None:
                        ninf += 1
                    else:
                        nfeas += 1; mok = False
                        print(f'  FEAS@t={f:.3f} m={m} cnt={cnt} k={k} {tier}', flush=True)
        print(f'm={m} 扫完（{"全 INF" if mok else "有 FEAS"}；{time.time()-t0:.0f}s；INF {ninf} FEAS {nfeas}）',
              flush=True)
    pf.close()
    print(f'\n扩扫收官：INF {ninf} / FEAS {nfeas}')


if __name__ == '__main__':
    main()
