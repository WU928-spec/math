"""联合交换引理探针（主代理手证第二步）——E 叶证书的核心。
问题：固定 cnt，任意装箱能否经"不增有序箱和向量"的局部交换到达唯一极小形（=E 叶的规范形）？
做法：随机初始装箱 → 贪心局部交换下降（swap 两箱间物品 / senior 跨型移动）→ 记录到达的局部极小形；
     多次随机起点是否收敛到同一结构（唯一性=叶规范形良定义）。
"""
import random
from itertools import combinations


def bins_of(assignment, items):
    """assignment: list of bin indices per item."""
    nb = max(assignment) + 1
    bins = [[] for _ in range(nb)]
    for i, b in enumerate(assignment):
        bins[b].append(items[i])
    return bins


def sorted_sums(bins):
    return tuple(sorted(round(sum(b), 9) for b in bins))


def feasible(bins, cap=1.0):
    return all(sum(b) <= cap + 1e-9 for b in bins)


def exchanges(bins):
    """生成所有单物品跨箱移动与两物品跨箱交换的邻居。"""
    nb = len(bins)
    for i in range(nb):
        for j in range(i + 1, nb):
            for x in range(len(bins[i])):
                # 单移动 i->j
                yield ('move', i, j, x, None)
                for y in range(len(bins[j])):
                    yield ('swap', i, j, x, y)


def apply(bins, op):
    kind, i, j, x, y = op
    b = [list(bb) for bb in bins]
    if kind == 'move':
        b[j].append(b[i].pop(x))
    else:
        b[i][x], b[j][y] = b[j][y], b[i][x]
    return b


def descent(items, cap=1.0, max_steps=200):
    """从全放入一箱开始贪心下降到局部极小（保持可行）。"""
    n = len(items)
    bins = [list(items)]
    steps = 0
    while steps < max_steps:
        cur = sorted_sums(bins)
        best_op, best_sums = None, cur
        for op in exchanges(bins):
            nb = apply(bins, op)
            if not feasible(nb, cap):
                continue
            s = sorted_sums(nb)
            if s < best_sums:   # 字典序严格下降 = 更均衡
                best_op, best_sums = op, s
        if best_op is None:
            break
        bins = apply(bins, best_op)
        steps += 1
    return bins, steps


def structure(bins):
    """记录极小形的结构：按值排序的物品组合（忽略箱标号）。"""
    return tuple(sorted(tuple(sorted(round(v, 6) for v in b)) for b in bins))


if __name__ == '__main__':
    random.seed(23)
    from collections import Counter
    structs = Counter()
    n_struct_items = 0
    trials = 0
    mismatch = 0
    prev_struct = None
    for trial in range(400):
        m = random.choice([4, 5, 6])
        n = m + random.choice([0, 1])
        items = sorted(random.uniform(0.2, 0.7) for _ in range(n))
        bins, steps = descent(items)
        st = structure(bins)
        structs[st] += 1
        trials += 1
        if prev_struct is not None and st != prev_struct:
            # 不同实例当然不同结构；这里只看同实例多起点——改做同实例多起点：
            pass
        prev_struct = st
    print(f'{trials} 实例到达 {len(structs)} 种局部极小结构（跨实例）')
    # 同实例多起点唯一性
    uniq_fail = 0
    for trial in range(120):
        m = random.choice([4, 5])
        n = m + random.choice([0, 1])
        items = sorted(random.uniform(0.2, 0.7) for _ in range(n))
        got = set()
        for _ in range(6):
            random.shuffle(items)
            bins, _ = descent(items)
            got.add(structure(bins))
        if len(got) > 1:
            uniq_fail += 1
            if uniq_fail <= 3:
                print(f'  多起点发散: items={[round(v,3) for v in sorted(items)]} -> {len(got)} 种极小形')
                for g in got:
                    print('   ', g)
    print(f'同实例 6 起点：{120 - uniq_fail}/120 收敛唯一')
