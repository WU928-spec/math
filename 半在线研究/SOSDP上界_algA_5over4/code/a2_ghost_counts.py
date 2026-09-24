"""a2_ghost_counts.py — 鬼影点计数快检 + b_min/b_max 校准。

任务1（最高优先）：洞区鬼影点对可装箱必要条件逐条核验：
  (a) 最小 2a seniors 极端配对 ≤1；(b) 最小 3d 池件可分 d 三元组 ≤1（精确 DFS）；
  (c) 最小 2e juniors 反序配对 ≤1；(d) SJ 链图最大匹配 ≥b（阈值图贪婪）；
  (e) 体积 ≤ m。另用 can_pack_fast 直接判可装箱性（对照）。
  ⚠️ 先验提醒：洞区 LP 鬼影点满足规范装箱帽 ⟹ 规范可装箱 ⟹ 必然满足全部必要条件；
  若全部通过则证明"计数行杀不了洞族"（与 a2_g1_flow.md §4 一致）。任何违反立即 FLAG。
任务2（次优先）：b_min/b_max 校准——小尺寸全枚举可达 b 集合 vs 公式：
  b_max = 链图 SJ 最大匹配数（阈值图贪婪精确）；b_min 候选 = max(δ_s, δ_j) 的奇偶修正，
  δ_Q = max_L [#{Q≥L} − #{Q≤1−L}]_+。
"""
import numpy as np
from itertools import combinations
from functools import lru_cache
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hole_diag import primal_point
from hole_close import holes_of
from a2_transfer_falsifier_v2 import can_pack_fast


def triple_packable(items, d):
    """最小 3d 件可否分 d 三元组 ≤1（精确 DFS，小尺寸）。"""
    items = sorted(items)[:3 * d]
    n = len(items)

    @lru_cache(maxsize=None)
    def dfs(mask):
        if mask == 0:
            return True
        i = (mask & (-mask)).bit_length() - 1
        rest = mask ^ (1 << i)
        others = []
        mm = rest
        while mm:
            lsb = mm & (-mm)
            others.append(lsb.bit_length() - 1)
            mm ^= lsb
        for u, v in combinations(others, 2):
            if items[i] + items[u] + items[v] <= 1 + 1e-9 and dfs(rest ^ (1 << u) ^ (1 << v)):
                return True
        return False
    return dfs((1 << n) - 1)


def max_sj_matching(seniors, juniors):
    """阈值二分图（边 s+j≤1）最大匹配——链图嵌套邻域，升序贪婪精确。"""
    s_sorted = sorted(seniors, reverse=True)
    j_sorted = sorted(juniors)
    used = [False] * len(j_sorted)
    cnt = 0
    for sv in s_sorted:   # 大 senior 优先配最小相容 junior
        for i, jv in enumerate(j_sorted):
            if not used[i] and sv + jv <= 1 + 1e-9:
                used[i] = True; cnt += 1; break
            if not used[i] and sv + jv > 1 + 1e-9:
                break
    return cnt


def ghost_conditions(x, m, cnt):
    """返回 dict 条件名→(bool, 细节)。"""
    nS = m - 1
    a, b, c, d, e, f = cnt
    p, t = x[0], x[1]
    s = sorted(x[2:2 + nS]); j = list(x[2 + nS:2 + 2 * nS])
    pool = sorted(j + [t])
    out = {}
    out['(a)SS极端配对'] = (all(s[i] + s[2 * a - 1 - i] <= 1 + 1e-9 for i in range(a)),
                           [round(s[i] + s[2 * a - 1 - i], 4) for i in range(a)])
    out['(b)JJJ最小3d可分'] = (triple_packable(pool, d), None)
    jj = pool[:2 * e]  # 最小 2e
    out['(c)JJ反序配对'] = (all(jj[i] + jj[2 * e - 1 - i] <= 1 + 1e-9 for i in range(e)), None)
    mm = max_sj_matching(s, pool)
    out['(d)SJ最大匹配>=b'] = (mm >= b, f'maxmatch={mm} b={b}')
    vol = p + sum(s) + sum(pool)
    out['(e)体积<=m'] = (vol <= m + 1e-9, round(vol, 4))
    return out


def task1():
    print('=== 任务1：洞区鬼影点逐条件核验（m=12..20）===')
    nviol = 0
    for m in range(12, 21):
        for cnt, k in holes_of(m):
            x = primal_point(m, cnt, k)
            if x is None:
                continue
            nS = m - 1
            p, t = x[0], x[1]
            s = list(x[2:2 + nS]); j = list(x[2 + nS:2 + 2 * nS])
            items = [p] + s + j + [t]
            pk = can_pack_fast(items, m)
            conds = ghost_conditions(x, m, cnt)
            bad = {nm: dt for nm, dt in conds.items() if not dt[0]}
            if bad:
                nviol += 1
                print(f'  ✗ m={m} cnt={cnt} k={k}: 违反 {list(bad)}（pack={pk}）', flush=True)
            if not pk:
                print(f'  注记 m={m} cnt={cnt} k={k}: DFS 判不可装箱（违反先验"规范可装"）', flush=True)
    print(f'任务1 汇总：违反必要条件的鬼影 {nviol} 个（0=计数行杀不了洞族，与先验一致）')


def task2():
    t_start2 = time.time()
    print('=== 任务2：b_min/b_max 校准（小尺寸全枚举）===')
    rng = np.random.default_rng(7)
    n_int = n_hole_int = 0
    bmax_bad = bmin_bad = 0
    examples = []
    while n_int < 400:
        nS = int(rng.integers(3, 6))
        N = nS + 1
        if (nS + N) % 2 == 1:
            continue
        t = float(rng.uniform(0.251, 1 / 3))
        S = sorted(rng.uniform(1 - 2 * t + 0.005, 0.75, nS))
        J = sorted(rng.uniform(t, 2 * t - 0.005, N))
        # 合并排序并携带类型标签（值重复时 senior 优先的标签规则仍歧义——改用索引对）
        tagged = [(v, True) for v in S] + [(v, False) for v in J]
        tagged.sort(key=lambda z: z[0])
        items = [v for v, _ in tagged]
        typ = [tg for _, tg in tagged]
        n = len(items)
        @lru_cache(maxsize=None)
        def dfs(mask):
            if mask == 0:
                return 1  # 位集：b=0 可达
            i = (mask & (-mask)).bit_length() - 1
            rest = mask ^ (1 << i)
            out = 0
            mm = rest
            while mm:
                lsb = mm & (-mm)
                jj = lsb.bit_length() - 1
                if items[i] + items[jj] <= 1 + 1e-9:
                    sub = dfs(rest ^ (1 << jj))
                    out |= (sub << 1) if (typ[i] ^ typ[jj]) else sub
                mm ^= lsb
            return out
        reach_bits = dfs((1 << n) - 1)
        if not reach_bits:
            continue
        reach = [b for b in range(n // 2 + 2) if reach_bits >> b & 1]
        n_int += 1
        bmin_r, bmax_r = reach[0], reach[-1]
        holes = [v for v in range(bmin_r, bmax_r + 1) if not (reach_bits >> v & 1) and (v - bmin_r) % 2 == 0]
        # b_max 公式：SJ 链图最大匹配
        bm = max_sj_matching(S, J)
        # 但 b_max 还受体积/配对余量限制：b_max = min(最大匹配, 体积侧...)
        if bm < bmax_r:
            bmax_bad += 1
            examples.append(('bmax公式低估', bmax_r, bm, [round(x, 3) for x in items]))
        # b_min 候选：max(δ_s, δ_j)（L>1/2 阈值）
        def delta(Q):
            d = 0
            for L in sorted(set(Q)):
                if L <= 0.5 + 1e-9:
                    continue
                d = max(d, sum(1 for x in Q if x >= L - 1e-9) - sum(1 for x in Q if x <= 1 - L + 1e-9))
            return d
        bmin_c = max(delta(S), delta(J))
        # 奇偶修正：b ≡ nS (mod 2)
        if (bmin_c - nS) % 2 == 1:
            bmin_c += 1
        if bmin_c != bmin_r:
            bmin_bad += 1
            examples.append(('bmin', bmin_r, bmin_c, [round(x, 3) for x in items],
                             [round(x, 3) for x in S], [round(x, 3) for x in J]))
        if holes:
            n_hole_int += 1
            examples.append(('区间破洞', bmin_r, bmax_r, holes, [round(x, 3) for x in items]))
    print(f'校准：{n_int} 个有匹配实例；区间破洞 {n_hole_int}；b_max 公式低估 {bmax_bad}；'
          f'b_min 公式不符 {bmin_bad}')
    for e in examples[:6]:
        print('  ', e)


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if cmd in ('all', 't1'):
        task1()
    if cmd in ('all', 't2'):
        task2()
