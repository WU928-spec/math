"""CDL 探针 v2——不再实现规范形，而是问结构问题：
对每个可行实例，取"有序箱和向量字典序最小"的最均衡装箱（componentwise 最小化器），
检验它的结构是否就是规范形（S1 极端配对 / G2a 最小 3d / SJ 反序）。
若最小化器恒为规范结构 = CDL  empirically 成立（规范形=最均衡=componentwise 最小）。
"""
import itertools, random


def all_binnings_labeled(items, m):
    """items: [(value, label)]；枚举全部分法，返回 (bins_labels, bins_sums) 列表。"""
    n = len(items)
    results = []

    def dfs(idx, bins_l, bins_s):
        if idx == n:
            results.append((tuple(tuple(b) for b in bins_l), tuple(bins_s)))
            return
        v, lab = items[idx]
        seen = set()
        for b in range(len(bins_l)):
            key = round(bins_s[b], 9)
            if key in seen:
                continue
            seen.add(key)
            if bins_s[b] + v <= 1 + 1e-12:
                dfs(idx + 1, bins_l[:b] + [bins_l[b] + [lab]] + bins_l[b + 1:],
                    bins_s[:b] + [bins_s[b] + v] + bins_s[b + 1:])

    dfs(0, [[] for _ in range(m)], [0.0] * m)
    return results


if __name__ == '__main__':
    random.seed(11)
    stats = {'ss_extreme': 0, 'ss_not': 0, 'jjj_small': 0, 'jjj_not': 0, 'total': 0}
    examples = []
    for trial in range(1200):
        m = random.choice([5, 6])
        nS = m - 1
        t = random.uniform(0.26, 0.33)
        s = sorted(random.uniform(1 - 2 * t, 0.75) for _ in range(nS))
        w = sorted(random.uniform(t, 2 * t) for _ in range(nS))
        items = [(v, f's{i}') for i, v in enumerate(s)] + [(v, f'w{i}') for i, v in enumerate(w)] + [(t, 't')]
        binnings = all_binnings_labeled(items, m)
        feas = [(bl, bs) for bl, bs in binnings if all(v <= 1 + 1e-9 for v in bs)]
        if not feas:
            continue
        # 最均衡 = 有序和向量字典序最小
        best_bl, best_bs = min(feas, key=lambda x: tuple(sorted(round(v, 9) for v in x[1])))
        # 结构检查：SS 对（双 senior 箱）的配对是否=最小 2a 的极端配对
        bins = best_bl
        ss_bins = [b for b in bins if all(l.startswith('s') for l in b)]
        ss_pairs = [tuple(sorted(b)) for b in ss_bins]
        a = len(ss_pairs)
        if 2 * a <= nS:
            expected_ss = set()
            sidx = [f's{i}' for i in range(nS)]
            for i in range(a):
                expected_ss.add(frozenset((sidx[i], sidx[2 * a - 1 - i])))
            actual_ss = set(frozenset(p) for p in ss_pairs)
        else:
            expected_ss = actual_ss = None
        # JJJ 箱内容是否=池（w+t）中最小 3d 个
        jjj_bins = [b for b in bins if len(b) == 3 and all(l.startswith('w') or l == 't' for l in b)]
        pool_sorted = sorted([(v, l) for v, l in items if l.startswith('w') or l == 't'])
        d = len(jjj_bins)
        expected_jjj = set(l for v, l in pool_sorted[:3 * d])
        actual_jjj = set(l for b in jjj_bins for l in b)
        stats['total'] += 1
        if actual_ss == expected_ss: stats['ss_extreme'] += 1
        else: stats['ss_not'] += 1
        if actual_jjj == expected_jjj: stats['jjj_small'] += 1
        else: stats['jjj_not'] += 1
        if (actual_ss != expected_ss or actual_jjj != expected_jjj) and len(examples) < 4:
            examples.append((m, t, [round(v, 3) for v in s], [round(v, 3) for v in w], a, d, actual_ss, expected_ss))
    print(f"可行实例 {stats['total']}")
    print(f"SS=最小2a极端配对: {stats['ss_extreme']}/{stats['total']}")
    print(f"JJJ=池最小3d:      {stats['jjj_small']}/{stats['total']}")
    for ex in examples:
        print('  反例形态:', ex)
