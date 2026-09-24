"""CDL（规范支配引理）数值探针——主代理手证第一步。
陈述：对坍缩角落的物品多重集（cnt 固定），规范装箱的有序箱和向量
      按分量 ≤ 一切合法装箱的有序箱和向量。
      （则 (W'') 由单调性得出：canonical 可行 ⟸ 任意可行）
本探针：随机生成小角落多重集 + 全部装箱枚举，检验"canonical 有序和向量分量最小"。
先证零件（S1/S2/G2a 已知），重点测**同时规范化**是否相容（唯一未证点）。
"""
import itertools, random
from fractions import Fraction as F


def all_binnings(items, bins_cap):
    """items: list of values; 枚举把 items 装入 len(bins_cap) 个容量箱的全部分法（箱可空、箱有序?——箱无序+物品按值不可区分去重太复杂，直接 DFS 记录 multiset of bin sums）。
    返回所有可行装箱的箱和多重集。"""
    n = len(items)
    results = set()

    def dfs(idx, bins):
        if idx == n:
            results.add(tuple(sorted(bins)))
            return
        v = items[idx]
        seen = set()
        for b in range(len(bins)):
            if bins[b] in seen:
                continue
            seen.add(bins[b])
            if bins[b] + v <= bins_cap[b] + 1e-12:
                dfs(idx + 1, bins[:b] + [bins[b] + v] + bins[b + 1:])

    dfs(0, [0.0] * len(bins_cap))
    return results


def canonical_binning(s, w, t, cnt, x=None, y=None):
    """按规范形装箱：seniors 升序 s、juniors 升序 w（值序）、t。
    S1: SS=最小2a 极端配对；S2: S=最大c；SJ=反序配对（最小 senior 配最大 junior）；
    G2a: JJJ 集合=池{t}+w 中值序最小 3d。
    返回箱和列表（float）。"""
    a, b, c, d, e, f = cnt
    items_s = sorted(s)
    pool = sorted(w + [t])
    bins = []
    idx_s = 0
    # SS: 最小 2a 的极端配对
    ss = items_s[:2 * a]
    for i in range(a):
        bins.append(ss[i] + ss[2 * a - 1 - i])
    idx_s = 2 * a
    # S: 最大 c
    srest = items_s[2 * a:]
    sc = srest[-c:] if c > 0 else []
    sj = srest[:b]
    for v in sc:
        bins.append(v)
    # SJ: 反序配对（最小 senior 配最大 junior）
    # G2a: JJJ 从池取 3d 最小
    jjj = pool[:3 * d]
    rest = pool[3 * d:]
    jj = rest[:2 * e]
    j = rest[2 * e:2 * e + f]
    assert len(sj) == b and len(jjj) == 3 * d and len(jj) == 2 * e and len(j) == f
    for i in range(b):
        bins.append(sj[i] + rest_j_for_sj(jjj, jj, j, i, b))
    for i in range(d):
        bins.append(jjj[3 * i] + jjj[3 * i + 1] + jjj[3 * i + 2])
    for i in range(e):
        bins.append(jj[2 * i] + jj[2 * i + 1])
    for v in j:
        bins.append(v)
    return bins


def rest_j_for_sj(jjj, jj, j, i, b):
    # SJ 的 junior 伙伴：池去掉 JJJ/JJ/J 后的部分——此处简化为值序剩余
    pool_after = sorted(jjj + jj + j)
    avail = pool_after  # 简化探针：SJ 伙伴从池后部取（大 junior 配小 senior=反序）
    return avail[len(avail) - 1 - i] if len(avail) > i else 0.0


if __name__ == '__main__':
    random.seed(7)
    bad = 0
    trials = 0
    for trial in range(3000):
        m = random.choice([5, 6, 7])
        nS = m - 1
        # 角落状物品：seniors>1-2t、juniors∈[t,2t)
        t = random.uniform(0.26, 0.33)
        s = sorted(random.uniform(1 - 2 * t, 0.75) for _ in range(nS))
        w = sorted(random.uniform(t, 2 * t) for _ in range(nS))
        # 随机合法 cnt
        cnts = []
        for a in range(1, 3):
            for b in range(0, 4):
                c = nS - 2 * a - b
                if c < 0: continue
                for d in range(0, 3):
                    for e in range(0, 3):
                        f = m - a - b - c - d - e
                        if f < 0: continue
                        if b + 3 * d + 2 * e + f != m: continue
                        cnts.append((a, b, c, d, e, f))
        if not cnts:
            continue
        cnt = random.choice(cnts)
        a, b, c, d, e, f = cnt
        items = s + w + [t]
        allbins = all_binnings(items, [1.0] * m)
        feas = [bb for bb in allbins if all(v <= 1 + 1e-9 for v in bb)]
        if not feas:
            continue
        trials += 1
        canon = tuple(sorted(canonical_binning(s, w, t, cnt)))
        feas_sorted = sorted(feas)
        # CDL：canonical 是否某个可行装箱（它本身应可行），且其有序向量分量 ≤ 一切可行
        best = min(feas)  # 字典序最小=最均衡
        if canon not in feas:
            bad += 1
            if bad <= 3:
                print(f'canonical 本身不可行! cnt={cnt} t={t:.3f}')
                print(f'  s={[round(v,3) for v in s]} w={[round(v,3) for v in w]}')
                print(f'  canon={[round(v,3) for v in canon]}')
        elif list(canon) != list(best):
            bad += 1
            if bad <= 5:
                print(f'CDL 违反: cnt={cnt} t={t:.3f}')
                print(f'  canon={ [round(v,3) for v in canon] }')
                print(f'  best ={ [round(v,3) for v in best] }')
                print(f'  s={[round(v,3) for v in s]} w={[round(v,3) for v in w]}')
    print(f'\n{trials} 个可行实例中 {bad} 个违反/异常')
