"""③试点: region-portability 猜想小规模验证。
K1 模板权重在'装箱行替换为各胞腔极小形箱'的角落 LP 上是否仍列平衡(A^T y=0)。
(m,cnt)=m=12 (2,7,0,1,1,0) k=5 (K1 区 k<=b=7)。极小形由 a1_jel_seg1 下降器多起点产出。
"""
import numpy as np, sys, os
from fractions import Fraction as F
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from farkas_fixed import build_fixed, MG
from a1_jel_seg1 import descent, canonical_bins, key_of, bin_type

M, CNT, K, T0 = 12, (2, 7, 0, 1, 1, 0), 5, 0.32
NS = M - 1; JJ = K - 1

def make_items(seed):
    rng = np.random.default_rng(seed)
    p = 0.70 + rng.random() * 0.02
    s = 0.42 + rng.random(NS) * 0.06
    j = T0 + rng.random(NS) * 0.05
    return [p, T0] + list(s) + list(j)

def minima_catalog(items, n_starts=8, seed=0):
    """多起点下降, 返回不同 key 的极小形列表(箱内容, 箱型)。"""
    big = set(items[2:2 + NS])
    can = canonical_bins(items, M, CNT)
    starts = [can]
    rng = np.random.default_rng(seed)
    for _ in range(n_starts):
        b = None
        for _ in range(30):
            cand = [list(x) for x in can]
            for _ in range(3):
                i, j2 = rng.integers(0, len(cand), 2)
                if i != j2 and cand[i] and cand[j2]:
                    xi = cand[i].pop(); xj = cand[j2].pop()
                    cand[i].append(xj); cand[j2].append(xi)
            if all(sum(x) <= 1 + 1e-9 for x in cand):
                b = cand; break
        if b is not None: starts.append(b)
    seen = {}
    for st in starts:
        p_, _, _ = descent(st, big)
        k = key_of(p_)
        if k not in seen:
            seen[k] = p_
    return list(seen.values())

def var_of(items):
    """物品值 -> 变量索引(p=0,t=1,s_i=2+i,j_i=2+NS+i)。重复值取首个未占用。"""
    idx = {}
    idx[items[0]] = 0; idx[items[1]] = 1
    for i in range(NS): idx[items[2 + i]] = 2 + i
    for i in range(NS): idx[items[2 + NS + i]] = 2 + NS + i
    return idx

def cell_lp(minima, items):
    """角落 LP(build_fixed) 去装箱行 + 极小形的箱行(SS/SJ/JJJ/JJ 按物品值映射回变量)。"""
    A, bc, bt, names, nv = build_fixed(M, CNT, K)
    keep = [i for i, nm in enumerate(names) if nm not in ('SS', 'SJ', 'JJJ', 'JJ')]
    A2 = [A[i] for i in keep]; bc2 = [bc[i] for i in keep]
    bt2 = [bt[i] for i in keep]; n2 = [names[i] for i in keep]
    vmap = var_of(items)
    def add(bins_items, nm):
        r = [F(0)] * nv
        for v in bins_items:
            r[vmap[v]] += 1
        A2.append(r); bc2.append(F(1)); bt2.append(F(0)); n2.append(nm)
    for bi, b in enumerate(minima):
        t_ = bin_type(b, set(items[2:2 + NS]))
        nm = {(2, 0): 'SS', (1, 1): 'SJ', (0, 3): 'JJJ', (0, 2): 'JJ',
              (1, 0): 'S', (0, 1): 'J'}[t_]
        add(b, f'{nm}#{bi}')
    return A2, bc2, bt2, n2, nv

# K1 模板权重 (midk_note §8.1)
K1 = [('danger', 8), ('pair0', 4), ('pair1', 4), ('j0<=q1', 4), ('j1<=q1', 4),
      ('t<=q1', 2), ('q1<=am', 1), ('q1<=j4', 4), ('nofit8', 2),
      ('SJj', 8), ('SS0', 4), ('JJJ0', 2), ('j>=t', 2), ('j>=t', 2), ('j>=t', 2)]

def port_check(A2, bc2, bt2, n2, nv, minima, items):
    """把 K1 权重映射到胞腔行并查 A^T y=0。"""
    vmap = var_of(items)
    rows = {}
    for i, nm in enumerate(n2):
        rows.setdefault(nm, []).append(i)
    def find(name_pred):
        for nm, lst in rows.items():
            if name_pred(nm):
                return lst
        return None
    y = [F(0)] * len(A2)
    used = set()
    def put(idxs, w):
        for ix in idxs:
            if ix not in used:
                used.add(ix); y[ix] = F(w); return True
        return False
    ok_map = True
    for nm, w in K1:
        if nm == 'SJj':
            # q1 = j_jj 所在 SJ 箱
            jj_bin = [b for b in minima if vmap[items[2 + NS + JJ]] in [vmap[v] for v in b]]
            tgt = None
            for bi, b in enumerate(minima):
                if items[2 + NS + JJ] in b and bin_type(b, set(items[2:2 + NS])) == (1, 1):
                    tgt = f'SJ#{bi}'; break
            if tgt is None or not put(rows.get(tgt, []), w): ok_map = False
        elif nm == 'SS0':
            ss = [f'SS#{bi}' for bi, b in enumerate(minima)
                  if bin_type(b, set(items[2:2 + NS])) == (2, 0)]
            if not ss or not put(rows.get(ss[0], []), w): ok_map = False
        elif nm == 'JJJ0':
            jj = [f'JJJ#{bi}' for bi, b in enumerate(minima)
                  if bin_type(b, set(items[2:2 + NS])) == (0, 3)]
            if not jj or not put(rows.get(jj[0], []), w): ok_map = False
        elif nm == 'j>=t':
            cand = [i for i, nmx in enumerate(n2) if nmx.startswith('j') and nmx.endswith('>=t')
                    and i not in used]
            if cand: used.add(cand[0]); y[cand[0]] = F(w)
            else: ok_map = False
        elif nm == 'q1<=j4':
            if not put(rows.get('q1<=j4', []), w): ok_map = False
        else:
            if not put(rows.get(nm, []), w): ok_map = False
    if not ok_map:
        return None, '行映射失败'
    bad_cols = [j for j in range(nv) if sum(A2[i][j] * y[i] for i in range(len(y))) != 0]
    return (y, bad_cols), f'映射OK, 列破坏={len(bad_cols)} 列'

if __name__ == '__main__':
    items = make_items(11)
    mins = minima_catalog(items, n_starts=10, seed=1)
    for mn in mins:
        print('极小形:', [[round(v,3) for v in b] for b in mn])
    print(f'极小形(胞腔)数: {len(mins)}')
    for ci, mn in enumerate(mins[:3]):
        A2, bc2, bt2, n2, nv = cell_lp(mn, items)
        res, msg = port_check(A2, bc2, bt2, n2, nv, mn, items)
        print(f'胞腔{ci}: {msg}', flush=True)
        if res and res[1]:
            print('   破坏列:', res[1][:6])
