"""JEL 第①段: cnt/型保持下降（交换邻域扩展: 单物品移动+两物品交换+cnt-保持跨型移动）。
实测 m=6..12 角落多重集: (a) 终止性 (b) 多起点唯一性 (c) 极小形 vs LP 规范行同型。
势 = 有序箱和向量(降序)字典序严格降。
"""
import numpy as np, itertools, sys, os
from scipy.optimize import linprog
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hole_close import build_close
from a2_transfer_falsifier_v2 import can_pack_fast
from fractions import Fraction as F

def bin_type(b, big_set):
    n_big = sum(1 for x in b if x in big_set)
    return (n_big, len(b) - n_big)

def cnt_of(bins, big_set):
    from collections import Counter
    c = Counter()
    for b in bins:
        t_ = bin_type(b, big_set)
        c[t_] += 1
    return c

def key_of(bins):
    return tuple(sorted((sum(b) for b in bins), reverse=True))

def moves(bins, big_set):
    """cnt-保持邻域: 同型箱间单物品移动/交换 + 跨型交换(SS<->SJ, SJ<->JJ, JJJ<->JJ, SS<->S)。全部保持箱数与 cnt。"""
    n = len(bins)
    c0 = cnt_of(bins, big_set)
    cands = []
    for i in range(n):
        for j in range(i + 1, n):
            # 跨箱单物品移动(若型计数不变)
            for xi in list(bins[i]):
                nb = [list(b) for b in bins]
                nb[i].remove(xi); nb[j].append(xi)
                if all(nb_ for nb_ in nb) and cnt_of(nb, big_set) == c0:
                    cands.append(nb)
            # 两物品交换
            for xi in list(bins[i]):
                for xj in list(bins[j]):
                    nb = [list(b) for b in bins]
                    nb[i].remove(xi); nb[i].append(xj)
                    nb[j].remove(xj); nb[j].append(xi)
                    if cnt_of(nb, big_set) == c0:
                        cands.append(nb)
    return cands

def descent(bins0, big_set, max_steps=500):
    bins = [list(b) for b in bins0]
    for _ in range(max_steps):
        k0 = key_of(bins)
        best = None
        for nb in moves(bins, big_set):
            kn = key_of(nb)
            if kn < k0 and (best is None or kn < key_of(best)):
                best = nb
        if best is None:
            return bins, True, _
        bins = best
    return bins, False, max_steps

def ffd(items, m):
    it = sorted(items, reverse=True)
    bins = []
    for w in it:
        for b in bins:
            if sum(b) + w <= 1 + 1e-9:
                b.append(w); break
        else:
            if len(bins) >= m: return None
            bins.append([w])
    return bins

def canonical_bins(items, m, cnt):
    p_, t_ = items[0], items[1]
    nS = (len(items) - 2) // 2
    a, b, c, d, e, f = cnt
    s = sorted(items[2:2 + nS]); j = list(items[2 + nS:2 + 2 * nS]) + [t_]
    bins = [[p_]]
    for i in range(a): bins.append([s[2*i], s[2*i+1]])
    for i in range(b): bins.append([s[2*a+i], j[i]])
    si = b
    for i in range(d): bins.append([j[si], j[si+1], j[si+2]]); si += 3
    for i in range(e): bins.append([j[si], j[si+1]]); si += 2
    for i in range(f): bins.append([j[si]]); si += 1
    return bins

def corner_items(m, cnt, k, t0, rng):
    """直接构造角落实: senior>1-2t, junior∈[t,2t), pair s_i+j_i>=p, p+t>5/4, L<=1 型约束。"""
    nS = m - 1
    # pair-tight 构造: s_i+j_i=p(窄幅抖动), p≈5/4-t, j∈[t,2t), s>1-2t 自动(下验证)
    for _ in range(300):
        p = 5 / 4 - t0 + 0.004 + rng.random() * 0.012
        j = t0 + rng.random(nS) * t0 * 0.85
        s = p - j + (rng.random(nS) - 0.5) * 0.02
        if np.all(s + j >= p) and np.all(s > 1 - 2 * t0) and np.all(s <= 1) and p <= 1:
            items = [p, t0] + list(s) + list(j)
            if sum(items) <= m - 0.01 and ffd(items, m) is not None:
                return items
    return None

def canon_key_equal(b1, b2):
    return key_of(b1) == key_of(b2)

if __name__ == '__main__':
    from collections import Counter
    def construct(m, rng):
        """可行构造: {p} 独占, {t, j_a, j_b}(两最小 j), 其余 nS-2 senior 各配一 junior
        (配对窗口 [p-s, 1-s] 非空采样), 多余 senior 独箱。箱数 = 1+1+(nS-2) = m-1。"""
        nS = m - 1; t0 = 0.32
        p = 0.88 + rng.random() * 0.02   # 松弛 danger（紧角落实为 razor, 见文档）
        pass
        j = t0 + rng.random(nS) * 0.02
        s = p - j + (rng.random(nS) - 0.5) * 0.004   # pair-tight, 窄带
        lo = np.maximum(p - s, t0); hi = 1 - s
        if np.any(lo > hi): return None
        js = list(j)
        bins = [[p]]
        # t 配两最小 j
        js.sort()
        if t0 + js[0] + js[1] > 1: return None
        bins.append([t0, js[0], js[1]])
        rest = js[2:]
        used = [False] * nS
        # 每个剩余 junior 配一台 senior(s+j∈[p,1])
        for jj in sorted(rest, reverse=True):
            best = None
            for i in range(nS):
                if not used[i] and p - 1e-9 <= s[i] + jj <= 1 + 1e-9:
                    if best is None or s[i] > s[best]: best = i
            if best is None: return None
            used[best] = True; bins.append([s[best], jj])
        for i in range(nS):
            if not used[i]: bins.append([s[i]])
        if len(bins) > m: return None
        items = [p, t0] + list(s) + list(j)
        return items, bins

    for m in [6, 8, 12]:
        n = term = uniq = styp = ncon = 0
        for trial in range(40):
            rng = np.random.default_rng(7000 + trial * 17 + m)
            out = construct(m, rng)
            if out is not None: ncon += 1
            if out is None: continue
            items, bins0 = out
            big_set = set(items[2:2 + m - 1])
            p_f, t_f, _ = descent(bins0, big_set)
            # 随机可行扰动起点
            b0 = None
            for _ in range(20):
                cand0 = [list(b) for b in bins0]
                for _ in range(2):
                    i, j2 = rng.integers(0, len(cand0), 2)
                    if i != j2 and cand0[i] and cand0[j2]:
                        xi = cand0[i].pop(); xj = cand0[j2].pop()
                        cand0[i].append(xj); cand0[j2].append(xi)
                if all(sum(b) <= 1 + 1e-9 for b in cand0):
                    b0 = cand0; break
            if b0 is None: continue
            p_r, t_r, _ = descent(b0, big_set)
            n += 1; term += (t_f and t_r)
            uniq += canon_key_equal(p_f, p_r)
            tf = tuple(sorted(Counter(bin_type(b, big_set) for b in p_f).items()))
            tr = tuple(sorted(Counter(bin_type(b, big_set) for b in p_r).items()))
            styp += (tf == tr)
        print(f'm={m}: 构造{ncon} 实例{n} 终止{term}/{n} 同极小{uniq}/{n} 同型{styp}/{n}', flush=True)
