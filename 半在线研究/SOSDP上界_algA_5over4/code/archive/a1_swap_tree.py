"""思路 E 原型：换位分支树（(W'') 弱叶）—— tiered ghost 壳 m=12 (3,11,0,1,2,0)。
树：内节点=hi 区 junior 机器序指派（换位），叶=(W'') 弱判定（任意可装⟹规范可装）。
弱叶验证：对每个换位指派 pi，解角落 LP 取点，DFS 任意装箱 + 规范装箱双侧检查。
"""
import numpy as np, itertools, sys, os
from scipy.optimize import linprog
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hole_close import build_close
from a2_transfer_falsifier_v2 import can_pack_fast

def corner_point(m, cnt, k, t0):
    A, bc, bt, names, nv = build_close(m, cnt, k, use_mon2=False, use_ammin=False)
    Af = np.array([[float(z) for z in row] for row in A])
    bf = np.array([float(bc[i]) + float(bt[i]) * t0 for i in range(len(A))])
    res = linprog(c=np.zeros(nv), A_ub=Af, b_ub=bf, bounds=(None, None), method='highs')
    return (res.status, res.x) if res.status == 0 else (res.status, None)

def canonical_packable(items, m, cnt):
    """口袋2 规范装箱：p 独占；senior 升序相邻配对 SS；SJ 按 junior 机器序池；JJJ/JJ/J; t 殿后。
    计数 (a,b,c,d,e,f) 直接由 cnt 读入（口袋2 守恒 2a+b+c=nS, b+3d+2e+f=nS+1）。"""
    p, t_ = items[0], items[1]
    nS = (len(items) - 2) // 2
    a, b, c, d, e, f_ = cnt
    s = sorted(items[2:2 + nS])  # 升序(口袋2 srt)
    j = list(items[2 + nS:2 + 2 * nS]) + [t_]
    bins = [[p]]
    for i in range(a):
        bins.append([s[2 * i], s[2 * i + 1]])
    for i in range(b):
        bins.append([s[2 * a + i], j[i]])
    si = b
    for i in range(d):
        bins.append([j[si], j[si + 1], j[si + 2]]); si += 3
    for i in range(e):
        bins.append([j[si], j[si + 1]]); si += 2
    for i in range(f_):
        bins.append([j[si]]); si += 1
    return all(sum(bb) <= 1 + 1e-9 for bb in bins)

def swap_tree(m, cnt, k, t0):
    nS = m - 1; jj = k - 1
    st, x = corner_point(m, cnt, k, t0)
    if st != 0:
        return None
    items0 = list(x[:2 + 2 * nS])
    hi = list(range(jj + 1, nS))          # hi 区机器
    j_idx = [2 + nS + i for i in hi]       # hi 区 junior 变量下标
    jvals = [x[i] for i in j_idx]
    leaves = []
    for perm in itertools.permutations(range(len(hi))):
        items = list(items0)
        for slot, src in enumerate(perm):
            items[j_idx[slot]] = jvals[src]
        any_pack = can_pack_fast(list(items), m)
        canon = canonical_packable(items, m, cnt)
        leaves.append((perm, any_pack, canon))
    return leaves

if __name__ == '__main__':
    m, cnt = 18, (3, 11, 0, 1, 2, 0)
    nS = m - 1
    for k in [15, 16, 17]:
        jj = k - 1
        h = nS - 1 - jj
        for t0 in [0.315, 0.322, 0.328, 0.332]:
            leaves = swap_tree(m, cnt, k, t0)
            if leaves is None:
                print(f'k={k} t={t0}: LP 不可行'); continue
            n = len(leaves)
            bad = [L for L in leaves if L[1] and not L[2]]   # 任意可装但规范不可装 = 弱叶破
            ok = all((not L[1]) or L[2] for L in leaves)
            print(f'k={k} (jj={jj}, h={h}) t={t0}: 叶数={n} (={h}!), '
                  f'(W\'\')弱叶 {"全过" if ok else f"破{len(bad)}"} '
                  f'[any={sum(L[1] for L in leaves)} canon={sum(L[2] for L in leaves)}]')
