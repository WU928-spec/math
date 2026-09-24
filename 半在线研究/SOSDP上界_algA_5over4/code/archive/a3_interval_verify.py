"""a3_ 区间定理独立核验（对拍主代理 358 例 probe）。
阈值图：物品排序值 x_1<=..<=x_n（n 偶），边 (i,j) ⟺ x_i+x_j<=1。
完美匹配的"交叉边数" b：把物品分为两类（senior/junior 标签），
b = #{边 (u,v): 两端类型不同}。区间定理断言：可行完美匹配的可达 b 集 = 带奇偶区间。
核验：枚举全部完美匹配（n<=8 穷举），算 b 值集合，检查区间+奇偶。
"""
import sys, os, random, itertools


def perfect_matchings(items, cap=1.0):
    """全部可行完美匹配（n 偶）。返回 [frozenset of (i,j)]。"""
    n = len(items)
    out = []
    def dfs(rest, cur):
        if not rest:
            out.append(frozenset(cur)); return
        i = rest[0]
        for k in range(1, len(rest)):
            j = rest[k]
            if items[i] + items[j] <= cap + 1e-9:
                dfs(rest[1:k] + rest[k+1:], cur + [(i, j)])
    dfs(list(range(n)), [])
    return out


def b_of(matching, types):
    return sum(1 for i, j in matching if types[i] != types[j])


def check_instance(vals, types, tag=''):
    """vals 升序值，types 0/1 标签。返回 (n_match, b_set, 区间性ok)。"""
    ms = perfect_matchings(vals)
    if not ms:
        return None
    bs = sorted(set(b_of(m, types) for m in ms))
    ok = bs == list(range(bs[0], bs[-1] + 1, 2)) if bs else True
    return (len(ms), bs, ok)


def main():
    random.seed(23)
    n_bad = 0; n_tot = 0; n_nomatch = 0
    for trial in range(400):
        n = random.choice([4, 6, 8])
        # 阈值图窗口分布（值 ∈ [0.2, 0.8]，cap=1）
        vals = sorted(random.uniform(0.2, 0.8) for _ in range(n))
        # 类型标签：随机 split（senior/junior）
        types = [0] * (n // 2) + [1] * (n - n // 2)
        random.shuffle(types)
        # 角落型标签：seniors=大件区、juniors=小件区（按值分层）
        if trial % 2 == 0:
            types = [1 if v < 0.5 else 0 for v in vals]  # 小件=junior
        r = check_instance(vals, types)
        if r is None:
            n_nomatch += 1; continue
        nm, bs, ok = r
        n_tot += 1
        if not ok:
            n_bad += 1
            print(f'  ✗ 破洞: vals={[round(v,3) for v in vals]} types={types} b集={bs}')
    print(f'核验：{n_tot} 个有匹配实例，无匹配 {n_nomatch}，区间性破洞 {n_bad}')
    print('判决:', '区间性全成立 ✓（与主代理 358 例 probe 一致）' if n_bad == 0 else f'{n_bad} 破洞 ✗✗')


if __name__ == '__main__':
    main()
