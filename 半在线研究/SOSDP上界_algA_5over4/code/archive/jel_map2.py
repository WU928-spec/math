"""JEL 分片测绘 v2——带索引跟踪的极小形结构测绘。
看极小形的组合类型（按物品索引的划分）随值变化的分片数与边界。
"""
import random


def descent_idx(items, m, cap=1.0, max_steps=300):
    """items: [(value, idx)]，m 个箱；贪心不增交换到局部极小。"""
    bins = [list(items)]
    n = len(items)

    def ssums(bs):
        return tuple(sorted((round(sum(v for v, _ in b), 9) for b in bs), reverse=True))

    def feas(bs):
        return all(sum(v for v, _ in b) <= cap + 1e-9 for b in bs)

    steps = 0
    while steps < max_steps:
        cur = ssums(bins)
        best = None
        nb_bins = len(bins)
        for i in range(nb_bins):
            for j in range(i + 1, nb_bins):
                for x in range(len(bins[i])):
                    cand = [list(b) for b in bins]
                    cand[j].append(cand[i].pop(x))
                    if feas(cand):
                        s = ssums(cand)
                        if s < cur:
                            best, cur = cand, s
                            break
                    for y in range(len(bins[j])):
                        cand = [list(b) for b in bins]
                        cand[i][x], cand[j][y] = cand[j][y], cand[i][x]
                        if feas(cand):
                            s = ssums(cand)
                            if s < cur:
                                best, cur = cand, s
                    if best is not None and ssums(best) == cur:
                        break
            if best is not None and ssums(best) == cur:
                break
        if best is None:
            break
        bins = best
        steps += 1
    return bins


def idx_struct(bins):
    return tuple(sorted(tuple(sorted(i for v, i in b)) for b in bins))


GRID = 20
a, d = 0.25, 0.70
regions = {}
pts = 0
for i in range(GRID):
    for j in range(i, GRID):
        b = a + (d - a) * (i + 1) / (GRID + 1)
        c = a + (d - a) * (j + 1) / (GRID + 1)
        items = sorted([(a, 0), (b, 1), (c, 2), (d, 3)])
        bins = descent_idx(items, 3)
        st = idx_struct(bins)
        regions.setdefault(st, 0)
        regions[st] += 1
        pts += 1
print(f'{pts} 网格点 → {len(regions)} 个极小形组合类型片区')
for st, cnt in sorted(regions.items(), key=lambda x: -x[1]):
    print(f'  {cnt:4d} 点: {st}')
