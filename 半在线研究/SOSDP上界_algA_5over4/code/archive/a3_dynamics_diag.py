"""a3_ 动力学主攻猜想诊断：razor 带角落点的值分层 vs 装箱穿针冲突。
主攻猜想（精确化）：razor 带角落 ⟹ 动力学同向绑定钉值分布 ⟹ 装箱穿针需求冲突 ⟹ 不可装箱。
诊断：提取 razor 带角落 LP（保序无装箱帽）可行点，值分层聚类，
装箱 DFS 找最大可装子集，报告失败的具体箱/层（冲突点解剖）。
"""
import numpy as np
from scipy.optimize import linprog
from fractions import Fraction as F
import sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fast_lp import rows_fixed

random.seed(23)


def best_pack_diag(items, nbins, cap=F(1)):
    """装箱 DFS：找最大可装件数 + 报告剩余装不下的件。"""
    items = sorted(items, reverse=True)
    best = [0, None]

    def dfs(i, bins):
        if i == len(items):
            if len(items) > best[0] or True:
                best[0] = len(items); best[1] = [list(b) for b in bins]
            return True
        # 先试放（保留更多件为目标：不可则跳过）
        x = items[i]
        seen = set()
        for b in bins:
            if len(b[1]) < 3 and b[0] + x <= cap and b[0] not in seen:
                seen.add(b[0])
                b[0] += x; b[1].append(x)
                if dfs(i + 1, bins):
                    return True
                b[0] -= x; b[1].pop()
        if len(bins) < nbins:
            bins.append([x, [x]])
            if dfs(i + 1, bins):
                return True
            bins.pop()
        # 跳过该件（记录不完全装箱）
        if best[0] < i + 1:
            best[0] = i  # 部分
        return False
    if sum(items) > nbins * cap:
        pass
    dfs(0, [])
    return best


def diag(m, k, t0):
    nS = m - 1
    R, nv = rows_fixed(m, (0, 0, nS, 0, 0, 0), k, use_order=True)
    R = [r for r in R if r[3] not in ('SS', 'SJ', 'JJJ', 'JJ')]
    Af = np.array([r for r, _, _, _ in R])
    bf = np.array([float(c0) + float(c1) * t0 for _, c0, c1, _ in R])
    res = linprog(c=np.zeros(nv), A_ub=Af, b_ub=bf, bounds=(None, None), method='highs')
    if res.status != 0:
        return None
    x = res.x
    s = x[2:2 + nS]; j = x[2 + nS:2 + 2 * nS]
    return x[0], x[1], s, j


def main():
    print('razor 带角落点值分层 + 装箱穿针冲突诊断')
    for m, k in [(6, 5), (8, 7), (12, 11)]:
        nS = m - 1
        tl = (m - 1) / (4 * (m - 2))
        for t0 in [tl + 0.01, 0.31, 0.33]:
            rec = diag(m, k, t0)
            if rec is None:
                print(f'  m={m} k={k} t={t0}: LP 不可行'); continue
            p, t, s, j = rec
            # 值分层聚类
            items = list(s) + list(j) + [t]
            uniq = sorted(set(round(v, 3) for v in items))
            print(f'  m={m} k={k} t={t0:.3f}: p={p:.4f} p+t={p+t:.4f} 值层={len(uniq)} 层')
            print(f'      seniors 层: {sorted(set(round(v,3) for v in s))}')
            print(f'      juniors 层: {sorted(set(round(v,3) for v in j))}')
            # 装箱
            fr = [F(str(v)).limit_denominator(10**6) for v in items]
            nfull = len(items)
            # 完整装箱判定
            from audit_constraints import pack_exact
            pk = pack_exact(fr, m - 1)
            print(f'      装箱: {"可行 ✓" if pk else "不可行 ✗"}')
            if pk is None:
                # 体积账
                print(f'      rest 体积={float(sum(fr)):.4f} vs 容量 {m-1}；件数 {nfull} vs 3 件/箱上限 {3*(m-1)}')


if __name__ == '__main__':
    main()
