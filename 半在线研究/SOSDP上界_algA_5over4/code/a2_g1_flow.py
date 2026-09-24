"""a2_g1_flow.py — G1 的"无指派计数刻画"狩猎。

typed 可行性精确判定（小尺寸 mask DP）：m 箱、型计数 cnt=(a,b,c,d,e,f)、
seniors s（nS=m-1 个）、池 pool（m 个 = juniors+t）。p 独占另箱（不占 cnt）。
判定：DFS 装箱，箱成分须命中型预算（senior 数/junior 数 → SS/SJ/S/JJJ/JJ/J）。

计数条件阶梯（全部池级、免指派）：
  F0 体积：Σ ≤ m；
  F1 双边吸收流：∃x∈[0,b] 整数：β_s ≤ c+a+x ∧ β_j ≤ f+e+(b−x)，β=#{>1/2}；
  F2 F1 + 伙伴 Hall 细化：对阈值 L ∈ 实例值集：#{s≥L} ≤ c + #{s≤1−L} + #{j≤1−L}
     （大 senior 的去处：S 独箱 / SS 配小 senior / SJ 配小 junior——上界式）；
  F2' 对称 junior 侧：#{j≥L} ≤ f + #{j≤1−L} + #{s≤1−L}（JJ/J 吸收 + SJ 配小 senior）；
  F3 F2+F2' + JJJ 低位细化：#{pool ≤ L} ≥ 3·#{...} 类（JJJ 三件需小件）。
对拍：角落窗口随机实例（t∈(1/4,1/3)、seniors∈(1−2t,0.75]、juniors∈[t,2t)），
m≤8，万例。输出失配率与最小失配反例。
附带：鬼影点检验（洞区 LP 鬼影值是否违反某计数条件——违反则 Hall 行可直接杀洞）。
"""
import numpy as np
from functools import lru_cache
from itertools import combinations
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pairing_feasible import bin_count_solutions

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'a2_g1_flow_progress.jsonl')


def typed_feasible(s, pool, cnt):
    """mask DP 精确判定。seniors 索引 0..nS-1，池件索引 nS..nS+m-1。"""
    nS = len(s)
    items = list(s) + list(pool)
    n = len(items)
    a, b, c, d, e, f = cnt

    @lru_cache(maxsize=None)
    def dfs(mask, a, b, c, d, e, f):
        if mask == 0:
            return True
        i = (mask & (-mask)).bit_length() - 1
        is_s = i < nS
        rest = mask ^ (1 << i)
        # 箱含 i：补 0..2 件（同侧/对侧）
        others = []
        mm = rest
        while mm:
            lsb = mm & (-mm)
            others.append(lsb.bit_length() - 1)
            mm ^= lsb
        for r in (0, 1, 2):
            for extra in combinations(others, r):
                ns = is_s + sum(1 for x in extra if x < nS)
                nj = (1 + r) - ns
                sm = items[i] + sum(items[x] for x in extra)
                if sm > 1 + 1e-9:
                    continue
                ok_type = False
                na, nb, nc, nd, ne, nf = a, b, c, d, e, f
                if (ns, nj) == (2, 0) and a > 0: na -= 1; ok_type = True
                elif (ns, nj) == (1, 1) and b > 0: nb -= 1; ok_type = True
                elif (ns, nj) == (1, 0) and c > 0: nc -= 1; ok_type = True
                elif (ns, nj) == (0, 3) and d > 0: nd -= 1; ok_type = True
                elif (ns, nj) == (0, 2) and e > 0: ne -= 1; ok_type = True
                elif (ns, nj) == (0, 1) and f > 0: nf -= 1; ok_type = True
                if ok_type and dfs(rest ^ sum(1 << x for x in extra), na, nb, nc, nd, ne, nf):
                    return True
        return False
    return dfs((1 << n) - 1, a, b, c, d, e, f)


def count_family(s, pool, cnt, level):
    """计数条件族判定（level 1=F1 流, 2=+F2, 3=+F3）。F0 恒查。"""
    nS = len(s)
    m = nS + 1
    a, b, c, d, e, f = cnt
    if sum(s) + sum(pool) > m + 1e-9:
        return False
    if level < 1:
        return True
    bs = sum(1 for x in s if x > 0.5 + 1e-9)
    bj = sum(1 for x in pool if x > 0.5 + 1e-9)
    ok1 = any(bs <= c + a + x and bj <= f + e + (b - x) for x in range(0, b + 1))
    if not ok1:
        return False
    if level < 2:
        return True
    vals = sorted(set(list(s) + list(pool)))
    for L in vals:
        # senior 侧伙伴 Hall：#{s≥L} ≤ c + #{s≤1−L} + #{j≤1−L}（粗上界）
        n_big_s = sum(1 for x in s if x >= L - 1e-9)
        cap = c + sum(1 for x in s if x <= 1 - L + 1e-9) + sum(1 for x in pool if x <= 1 - L + 1e-9)
        if n_big_s > cap:
            return False
        n_big_j = sum(1 for x in pool if x >= L - 1e-9)
        capj = f + sum(1 for x in pool if x <= 1 - L + 1e-9) + sum(1 for x in s if x <= 1 - L + 1e-9)
        if n_big_j > capj:
            return False
    if level < 3:
        return True
    # JJJ 低位细化：JJJ 箱三件各 ≤1−2t'（t'=min pool）；#{pool ≤ 1−2t'} ≥ 3d
    tp = min(pool)
    if sum(1 for x in pool if x <= 1 - 2 * tp + 1e-9) < 3 * d:
        return False
    return True


def gen_window_instance(rng, m):
    nS = m - 1
    cnts = bin_count_solutions(m)
    cnt = cnts[int(rng.integers(len(cnts)))]
    t = float(rng.uniform(0.251, 1 / 3))
    s = sorted(rng.uniform(1 - 2 * t + 0.005, 0.75, nS))
    pool = sorted(rng.uniform(t, 2 * t - 0.005, m))
    return s, pool, cnt, t


def ghost_values(m, cnt, k):
    """洞区鬼影值（分层有理构造，见 a2_transfer_falsifier）。"""
    nS = m - 1
    t = 1 / 3
    a = max(1, round(nS * 4 / 11))
    bb = max(0, round(nS * 4 / 11))
    s = [0.5] * a + [7 / 12] * b_ if False else None
    return None


def main():
    t0 = time.time()
    rng = np.random.default_rng(20260923)
    budget = float(os.environ.get('A2_G1_BUDGET', '400'))
    stats = {(lv): [0, 0] for lv in [1, 2, 3]}   # [agree, mismatch]
    mism = []
    n_real = 0
    while time.time() - t0 < budget:
        m = int(rng.integers(4, 9))
        s, pool, cnt, t = gen_window_instance(rng, m)
        real = typed_feasible(s, pool, cnt)
        if real:
            n_real += 1
        for lv in [1, 2, 3]:
            cf = count_family(s, pool, cnt, lv)
            if cf == real:
                stats[lv][0] += 1
            else:
                stats[lv][1] += 1
                # 只关心 "计数通过但不可行"（刻画过宽）与 "计数拒绝但可行"（过窄）
                if real and not cf:
                    tag = '过窄(真可行被判不可行)'
                else:
                    tag = '过宽(计数满足但不可行)'
                if len(mism) < 400:
                    mism.append((tag, m, cnt, lv, [round(x, 3) for x in s], [round(x, 3) for x in pool]))
        if sum(v[0] + v[1] for v in stats.values()) % 2000 == 0:
            print(f'  ... {time.time()-t0:.0f}s {stats} real={n_real}', flush=True)
    print(f'=== 一致性统计（agree/mismatch）: {stats}; 真实可行率 {n_real} ===')
    # 最小失配反例（最小 m 优先）
    mism.sort(key=lambda z: (z[1], z[3]))
    for z in mism[:8]:
        print('  失配:', z)
    with open(OUT, 'a') as ff:
        ff.write(json.dumps({'ts': time.time(), 'stats': {str(k): v for k, v in stats.items()},
                             'mismatches': len(mism)}) + '\n')


if __name__ == '__main__':
    main()
