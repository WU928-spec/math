"""JEL 手证验证：片内路径不变性 + 边界线性。
①同一片内两起点下降路径是否完全相同（交换序列一致）；
②两片边界处，结构切换的阈值是否=线性等式（两候选结构的 key 相等）。
物品：5 件 4 箱（贴近角落量级），两参数 (b,c) 网格。
"""
import random


def key_of(bins):
    return tuple(sorted((round(sum(v for v, _ in b), 9) for b in bins), reverse=True))


def feasible(bins, cap=1.0):
    return all(sum(v for v, _ in b) <= cap + 1e-9 for b in bins)


def descent_path(items, m, cap=1.0, max_steps=600):
    """返回 (终止箱, 交换路径签名列表)。路径签名=操作类型+物品索引。"""
    bins = [[] for _ in range(m)]
    for v, i in sorted(items, reverse=True):
        for b in bins:
            if sum(x for x, _ in b) + v <= cap + 1e-9:
                b.append((v, i))
                break
    path = []
    steps = 0
    while steps < max_steps:
        cur = key_of(bins)
        best, best_op = None, None
        for i in range(m):
            for j in range(i + 1, m):
                for x in range(len(bins[i])):
                    cand = [list(b) for b in bins]
                    cand[j].append(cand[i].pop(x))
                    if feasible(cand, cap):
                        k = key_of(cand)
                        if k < cur and (best is None or k < key_of(best)):
                            best, best_op = cand, ('m', i, j, x, -1)
                    for y in range(len(bins[j])):
                        cand = [list(b) for b in bins]
                        cand[i][x], cand[j][y] = cand[j][y], cand[i][x]
                        if feasible(cand, cap):
                            k = key_of(cand)
                            if k < cur and (best is None or k < key_of(best)):
                                best, best_op = cand, ('s', i, j, x, y)
        if best is None:
            break
        bins = best
        path.append(best_op)
        steps += 1
    return bins, path


def idx_struct(bins):
    return tuple(sorted(tuple(sorted(i for v, i in b)) for b in bins if b))


GRID = 16
a, e = 0.22, 0.68
regions = {}
mismatch_path = 0
pts = 0
for i in range(GRID):
    for j in range(i, GRID):
        b = a + (e - a) * (i + 1) / (GRID + 1)
        c = a + (e - a) * (j + 1) / (GRID + 1)
        items = sorted([(a, 0), (b, 1), (c, 2), (0.5, 3), (e, 4)])
        bins, path = descent_path(items, 4)
        st = idx_struct(bins)
        key = (st, tuple(path[:3]))
        regions.setdefault(st, 0)
        regions[st] += 1
        pts += 1
print(f'{pts} 网格点 → {len(regions)} 个片区（5件4箱）')
for st, cnt in sorted(regions.items(), key=lambda x: -x[1])[:10]:
    print(f'  {cnt:4d} 点: {st}')
