"""a3_ JEL② v2：角落分布胞腔计数（修正——razor 区体积超，用窗口下界以下的可装箱角落型）。
生成：t 取窗口下界以下；seniors 低端近全等 s_lo、高端 s_hi；juniors pair 近紧 j_i≈p−s_i
但夹入窄带 [t,2t)；体积约束 Σ(s_i+j_i)+t ≤ m−1（可装箱必要）；packs_exact 筛选可装箱实例。
"""
import numpy as np
import sys, os, random, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jel_map3 import descent_idx, idx_struct
from audit_constraints import pack_exact
from fractions import Fraction as F

random.seed(23)


def corner_instance_packable(m, rng, max_try=300):
    """razor 型角落多重集（窗口下界以下 t，体积顶死附近），筛可装箱。"""
    nS = m - 1
    tl = (m - 1) / (4 * (m - 2))      # razor 窗口下界
    for _ in range(max_try):
        t = rng.uniform(0.26, min(tl, 1/3) - 0.005)
        p = rng.uniform(5/4 - t + 0.005, 1 - t/(m-1) - 0.005)   # danger 且体积兼容
        # seniors：低端近全等 s_lo、高端 s_hi
        nhi = rng.randint(0, nS - 1)
        s_lo = rng.uniform(1 - 2*t + 0.01, min(p, 0.6))
        s_hi = rng.uniform(s_lo, min(1.0, p))
        seniors = [s_lo] * (nS - nhi) + [s_hi] * nhi
        juniors = []
        ok = True
        for s_i in seniors:
            lo = max(t, p - s_i + 0.001)
            hi = 2 * t - 0.001
            if lo >= hi:
                ok = False; break
            juniors.append(min(rng.uniform(lo, hi), hi))
        if not ok:
            continue
        items = seniors + juniors + [t]
        if sum(items) > m - 1 + 1e-9:
            continue
        fr = [F(str(v)).limit_denominator(10**6) for v in items]
        if pack_exact(fr, m - 1) is None:
            continue
        return sorted([(v, i) for i, v in enumerate(items)], reverse=True)
    return None


def main():
    print('JEL② v2：可装箱角落型（窗口下界以下 razor 型，packs_exact 筛）胞腔计数')
    t0 = time.time()
    for m in [6, 7, 8, 9, 10]:
        rng = random.Random(2000 + m)
        regions = {}
        ngot = 0
        tries = 0
        while ngot < 40 and tries < 40:
            tries += 1
            items = corner_instance_packable(m, rng)
            if items is None:
                continue
            ngot += 1
            bins = descent_idx(items, m - 1)
            st = idx_struct(bins)
            regions[st] = regions.get(st, 0) + 1
        print(f'  m={m}: {ngot} 可装箱实例 → 极小形结构数 = {len(regions)}')
        for st, cnt in sorted(regions.items(), key=lambda x: -x[1])[:3]:
            print(f'      {cnt:3d} 例: {st}')
    print(f'({time.time()-t0:.0f}s)')


if __name__ == '__main__':
    main()
