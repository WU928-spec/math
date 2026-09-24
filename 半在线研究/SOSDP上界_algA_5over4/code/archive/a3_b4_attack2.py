"""a3_b4_attack2.py —— B4 敌意攻击 v2.1（τ 变量化窗口 + 逐 k 的 uncond 行集 −B4 −A2）。

攻击域 = uncond 115 证明行集（值坐标+A1+A3+B1/B2/B3+A5+LZ/HZ）去掉 B4（SUSPECT）与 A2（SUSPECT），
逐 (m,cnt,k,q,mode) 只解 ~3 个 LP（τ∈[tlo,1/3] 变量化，lo/hi/mid 三见证点）。
mode: 'c'=(iii) 裸（B4_q 违反直接有效性检验）；'a'=+j_{q+2}<=1−2t（逃逸a）；
      'b'=+s_1+s_{nS+1−q}<=1（逃逸b）。
见证点 DFS 精确装箱（nS 箱 cap1，池=seniors+juniors+t）。可装箱 ⟹ B4 INVALID。
"""
import numpy as np
from scipy.optimize import linprog
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a1_value_lp2 as V

MGF = 1e-4
BASE_KW = dict(use_sjrev=False, use_s1v=False, use_jjrev=False, use_b4=False, use_a2=False)


def build_rows(m, cnt, k, q, mode):
    nS = m - 1
    A, bc, bt, names, leg, nv = V.build(m, cnt, **BASE_KW)
    rows = [([float(x) for x in row], float(bc[i]), float(bt[i]))
            for i, row in enumerate(A)]
    vs = lambda r: 3 + (r - 1); vj = lambda r: 3 + nS + (r - 1)
    IP, IAM, IQ1 = 0, 1, 2
    # A5_i: p - s_i - j_{nS-k+i} <= -MG  ⟺  j_{nS-k+i} >= p - s_i + MG（与 main_cegar3 一致）
    for i in range(1, k + 1):
        row = [0.0] * nv; row[IP] = 1.0; row[vs(i)] = -1.0; row[vj(nS - k + i)] = -1.0
        rows.append((row, -MGF, 0.0))
    # LZ: 4s_k - 5am - q1 <= 0
    row = [0.0] * nv; row[vs(k)] = 4.0; row[IAM] = -5.0; row[IQ1] = -1.0
    rows.append((row, 0.0, 0.0))
    if k < nS:
        row = [0.0] * nv; row[vs(k + 1)] = -4.0; row[IAM] = 5.0; row[IQ1] = 1.0
        rows.append((row, -MGF, 0.0))
    # (iii): -j_{q+2} - s_{nS+1-q} <= -1-MG
    row = [0.0] * nv; row[vj(q + 2)] = -1.0; row[vs(nS + 1 - q)] = -1.0
    rows.append((row, -1.0 - MGF, 0.0))
    if mode == 'a':
        row = [0.0] * nv; row[vj(q + 2)] = 1.0
        rows.append((row, 1.0, -2.0))     # j_{q+2} <= 1-2t
    elif mode == 'b':
        row = [0.0] * nv; row[vs(1)] = 1.0; row[vs(nS + 1 - q)] = 1.0
        rows.append((row, 1.0, 0.0))
    # τ 变量化：A x - bt·τ <= bc
    Af = np.array([r + [-btt] for r, _, btt in rows])
    bcf = np.array([b for _, b, _ in rows])
    return Af, bcf, nv


def dfs_pack(items, nbins, cap=1.0, eps=1e-9, budget=300000):
    """节点预算内精确判定；超预算返回 None（未知， razor 近紧幻影聚集区）。"""
    items = sorted(items, reverse=True)
    loads = [0.0] * nbins
    state = [0]

    def rec(i):
        state[0] += 1
        if state[0] > budget:
            return None
        if i == len(items):
            return True
        seen = set()
        for b in range(nbins):
            if loads[b] in seen:
                continue
            if loads[b] + items[i] <= cap + eps:
                seen.add(loads[b])
                loads[b] += items[i]
                r = rec(i + 1)
                if r is None:
                    loads[b] -= items[i]
                    return None
                if r:
                    return True
                loads[b] -= items[i]
            if loads[b] == 0.0:
                break
        return False
    return rec(0)


def attack(m, cnt, k, q, mode):
    nS = m - 1
    Af, bcf, nv = build_rows(m, cnt, k, q, mode)
    tlo = (m - 1) / (4 * (m - 2))
    bounds = [(None, None)] * nv + [(tlo, 1 / 3)]
    xs = []
    for csign in [1.0, -1.0]:
        c = np.zeros(nv + 1); c[nv] = csign
        res = linprog(c=c, A_ub=Af, b_ub=bcf, bounds=bounds, method='highs')
        if res.status != 0:
            return 0, 0, 0, None
        xs.append(res.x)
    res = linprog(c=np.zeros(nv + 1), A_ub=Af, b_ub=bcf, bounds=bounds, method='highs')
    if res.status == 0:
        xs.append(res.x)
    vs = lambda r: 3 + (r - 1); vj = lambda r: 3 + nS + (r - 1)
    nw = len(xs); npack = 0; nunk = 0; samp = None
    for x in xs:
        items = [x[vs(r)] for r in range(1, nS + 1)] + \
                [x[vj(r)] for r in range(1, nS + 1)] + [x[nv]]
        r = dfs_pack(items, nS)
        if r is None:
            nunk += 1
            samp = samp or dict(m=m, cnt=cnt, k=k, q=q, mode=mode, unknown=True,
                                t=round(float(x[nv]), 4),
                                s=[round(float(x[vs(r)]), 4) for r in range(1, nS + 1)],
                                j=[round(float(x[vj(r)]), 4) for r in range(1, nS + 1)])
        elif r:
            npack += 1
            samp = dict(m=m, cnt=cnt, k=k, q=q, mode=mode, t=round(float(x[nv]), 4),
                        s=[round(float(x[vs(r)]), 4) for r in range(1, nS + 1)],
                        j=[round(float(x[vj(r)]), 4) for r in range(1, nS + 1)])
            break
    return nw, npack, nunk, samp


def main():
    t0 = time.time()
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'a3_b4_attack2.jsonl')
    done = set()
    if os.path.exists(path):
        for l in open(path):
            try:
                r = json.loads(l); done.add((r['m'], tuple(r['cnt']), r['k'], r['q'], r['mode']))
            except Exception:
                pass
        print(f'断点 {len(done)}，续跑', flush=True)
    pf = open(path, 'a')
    nwit = npack = nunk = 0
    for m in range(6, 21):
        for cnt in [(1, m - 3, 0, 1, 0, 0), (2, m - 5, 0, 1, 1, 0)]:
            a = cnt[0]; nS = m - 1
            for k in range(2, m - 2):
                for q in range(2 * a + 1, nS - 1):
                    for mode in ['c', 'a', 'b']:
                        if (m, tuple(cnt), k, q, mode) in done:
                            continue
                        nw, npack, nuk, samp = attack(m, cnt, k, q, mode)
                        nwit += nw; npack += npack; nunk += nuk
                        pf.write(json.dumps(dict(m=m, cnt=cnt, k=k, q=q, mode=mode,
                                                 wit=nw, pack=npack, unk=nuk)) + '\n'); pf.flush()
                        if npack:
                            print(f'  ★ 可装箱! {json.dumps(samp)}', flush=True)
                        elif nuk and samp:
                            print(f'  ? DFS超预算(未知) m={m} cnt={cnt} k={k} q={q} {mode} t={samp["t"]}', flush=True)
        print(f'm={m} 完成（{time.time()-t0:.0f}s，见证 {nwit} 可装箱 {npack} 未知 {nunk}）', flush=True)
    pf.close()
    print(f'\nv2.2 收官：见证 {nwit}，可装箱 {npack}，DFS未知 {nunk}')


if __name__ == '__main__':
    main()
