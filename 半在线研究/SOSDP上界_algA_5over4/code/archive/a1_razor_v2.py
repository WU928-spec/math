"""razor 带规范形 v2 probe（角落域实例）。
v2b: lex-min typed 装箱(有序箱和向量降序字典序最小) 的结构恒定性检测。
v2a: MRF 分流形(大 junior 先 JJ 再 SJ 伴) 可行性率。
实例: m=6..10, razor cnt (1,m-3,0,1,0,0)/(2,m-5,0,1,1,0), 角落域(bottleneck>=5/4-t+eps, pair 绑机)。
"""
import numpy as np, sys, os
from functools import lru_cache
from itertools import combinations
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def lexmin_typed(s, pool, cnt):
    """返回 (lex 最小有序箱和向量, 结构 key) 或 None。mask DP, 记忆最优后缀向量。"""
    nS = len(s); items = list(s) + list(pool); n = len(items)
    a0, b0, c0, d0, e0, f0 = cnt
    @lru_cache(maxsize=None)
    def dfs(mask, a, b, c, d, e, f):
        if mask == 0: return ((), ())
        i = (mask & (-mask)).bit_length() - 1
        is_s = i < nS
        rest = mask ^ (1 << i)
        others = []
        mm = rest
        while mm:
            lsb = mm & (-mm); others.append(lsb.bit_length() - 1); mm ^= lsb
        best = None
        for r in (0, 1, 2):
            for extra in combinations(others, r):
                ns = is_s + sum(1 for x in extra if x < nS)
                nj = (1 + r) - ns
                sm = items[i] + sum(items[x] for x in extra)
                if sm > 1 + 1e-9: continue
                na, nb, nc, nd, ne, nf = a, b, c, d, e, f
                if (ns, nj) == (2, 0) and a > 0: na -= 1
                elif (ns, nj) == (1, 1) and b > 0: nb -= 1
                elif (ns, nj) == (1, 0) and c > 0: nc -= 1
                elif (ns, nj) == (0, 3) and d > 0: nd -= 1
                elif (ns, nj) == (0, 2) and e > 0: ne -= 1
                elif (ns, nj) == (0, 1) and f > 0: nf -= 1
                else: continue
                sub = dfs(rest ^ sum((1 << x) for x in extra), na, nb, nc, nd, ne, nf)
                if sub is None: continue
                vec = tuple(sorted((sm,) + sub[0], reverse=True))
                if best is None or vec < best[0]:
                    best = (vec, ((i, extra),) + sub[1])
        return best
    return dfs((1 << n) - 1, a0, b0, c0, d0, e0, f0)

def struct_key(pack, nS):
    """结构 key: JJJ trio 的池值序 + SJ 匹配的 (senior 值序, junior 池值序) 集。"""
    jj = sorted(set(tuple(sorted(x[1] if isinstance(x[1], tuple) else x[1])) for x in []))  # placeholder
    return str(pack)

def gen_instance(m, cnt, rng):
    """razor 带角落域(关键澄清后): 双峰结构——小 senior(SS 料, ~0.47) +
    大 senior(SJ 料, ~0.63 配小 junior ~0.33) + 中 junior(~0.46 配小 senior)。
    瓶颈配对 >= 5/4-t; SS/JJJ 成形约束满足。"""
    nS = m - 1
    t0 = 0.25 + rng.random() * (1 / 3 - 0.25)
    p_min = 5 / 4 - t0 + 0.002
    a = cnt[0]
    n_ss = min(2 * a, nS - 1)
    for _ in range(200):
        s_small = 0.45 + rng.random(n_ss) * 0.04            # SS 对料
        s_big = 0.64 + rng.random(nS - n_ss) * 0.08         # SJ 料(配小 junior)
        s = np.concatenate([s_small, s_big])
        j_small = t0 + rng.random(max(2, nS // 3)) * 0.02   # JJJ 料(2-3 件)
        j_mid = 0.44 + rng.random(nS - len(j_small)) * 0.10
        # 结构化绑机: 小 junior->大 senior, 中 junior->小 senior
        nb = nS - n_ss
        jl = list(j_small) + list(j_mid)
        j = list(jl[:nb]) + list(jl[len(j_small):])   # 前 nb 件(最小)给大 senior
        j = np.array(j[:nS])
        if np.any(s + j < p_min): continue
        if n_ss >= 2 and s_small[0] + s_small[1] > 1: continue
        pool = list(j) + [t0]
        sm = sorted(pool)
        if sm[0] + sm[1] + sm[2] > 1: continue              # JJJ 成形
        p = max(5 / 4 - t0 + 0.004, float(np.min(s + j)) - 0.001)
        if p > 1: continue
        return s, pool, p, t0
    return None

if __name__ == '__main__':
    for m in [6, 8]:
        for cnt in [(1, m - 3, 0, 1, 0, 0), (2, m - 5, 0, 1, 1, 0)]:
            if cnt[1] < 0 or cnt[0] * 2 + cnt[1] + cnt[2] != m - 1: continue
            n_ok = n_struct_const = 0
            keys = []
            rng = np.random.default_rng(42 + m)
            for _ in range(12):
                inst = gen_instance(m, cnt, rng)
                if inst is None: continue
                s, pool, p, t0 = inst
                r = lexmin_typed(list(s), list(pool), cnt)
                if r is None: continue
                n_ok += 1
                # 结构 key: JJJ trio 的池索引集 + SJ 匹配对
                desc = r[1]
                trios = sorted(tuple(sorted(x[1])) for x in desc if len(x[1]) == 2 and x[0] >= len(s))
                sjm = sorted(tuple(sorted(x)) for x in desc if x[0] < len(s) and len(x[1]) == 1)
                keys.append((str(trios), str(sjm)))
            uniq = len(set(keys))
            print(f'm={m} cnt={cnt}: lex-min 可行 {n_ok}/12, 结构常数 {uniq==1 and n_ok or f"{uniq}类/{n_ok}"}', flush=True)
