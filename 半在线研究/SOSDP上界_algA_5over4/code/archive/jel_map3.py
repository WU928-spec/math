"""JEL 分片测绘 v3——降序字典序势（真正的最均衡）+ 索引跟踪 + 可行性断言。"""
GRID = 20
a, d = 0.25, 0.70


def key_of(bins):
    return tuple(sorted((round(sum(v for v, _ in b), 9) for b in bins), reverse=True))


def feasible(bins, cap=1.0):
    return all(sum(v for v, _ in b) <= cap + 1e-9 for b in bins)


def descent_idx(items, m, cap=1.0, max_steps=400):
    # FFD 初始化（降序首适配），保证可行起点
    bins = [[] for _ in range(m)]
    for v, i in sorted(items, reverse=True):
        for b in bins:
            if sum(x for x, _ in b) + v <= cap + 1e-9:
                b.append((v, i))
                break
        else:
            raise ValueError('FFD 失败（实例不可行?）')
    assert feasible(bins, cap)
    steps = 0
    while steps < max_steps:
        cur = key_of(bins)
        best = None
        for i in range(m):
            for j in range(m):
                if i == j:
                    continue
                for x in range(len(bins[i])):
                    cand = [list(b) for b in bins]
                    cand[j].append(cand[i].pop(x))
                    if feasible(cand, cap):
                        k = key_of(cand)
                        if k < cur and (best is None or k < key_of(best)):
                            best = cand
                    for y in range(len(bins[j])):
                        cand = [list(b) for b in bins]
                        cand[i][x], cand[j][y] = cand[j][y], cand[i][x]
                        if feasible(cand, cap):
                            k = key_of(cand)
                            if k < cur and (best is None or k < key_of(best)):
                                best = cand
        if best is None:
            break
        bins = best
        steps += 1
    assert feasible(bins, cap), f'终态不可行! {bins}'
    return bins


def idx_struct(bins):
    return tuple(sorted(tuple(sorted(i for v, i in b)) for b in bins if b))


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
