"""JEL 第③步：极小形结构随值变化的分片测绘。
两参数族（4 件物品 3 箱）：a≤b≤c≤d 中固定形状，扫 (b,c) 平面，
记录每点极小形的结构（哪几件同箱），看分片数与边界形状。
"""
import sys
sys.path.insert(0, '/Users/a123456/math/research/2026-09-19_algA_5over4/code')
from exchange_probe import descent


def index_structure(bins):
    """组合类型：按原始索引（排序后 0..n-1）的划分，忽略箱标号与箱内顺序。"""
    return tuple(sorted(tuple(sorted(b)) for b in bins))


GRID = 24
for trial in range(3):
    a, d = 0.25, 0.70
    regions = {}
    pts = 0
    for i in range(GRID):
        for j in range(i, GRID):
            b = a + (d - a) * (i + 1) / (GRID + 1)
            c = a + (d - a) * (j + 1) / (GRID + 1)
            if c < b: continue
            items = sorted([a, b, c, d])
            bins, _ = descent(items)
            st = index_structure(bins)
            regions.setdefault(st, 0)
            regions[st] += 1
            pts += 1
    print(f'trial：{pts} 网格点, {len(regions)} 个极小形组合类型片区')
    for st, cnt in sorted(regions.items(), key=lambda x: -x[1])[:8]:
        print(f'  {cnt:4d} 点: {st}')
